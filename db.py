"""
Low-level functions for directly handling the database.
"""
import sqlite3
# TODO replace all datetime objects with date objects
from datetime import datetime
from re import match

from utilities import db_convert_match_criteria_to_string, parse_date_string_to_date_object

# TODO P3 make sure to take care of cases when food dependencies are deleted later.
# TODO P4 convert datetime objects to date objects


def create_db_and_tables(db_connection) -> None:
    """
    Creates the database with the two separate tables.

    This function probably only needs to be run once.
    """

    c = db_connection.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS record (
            date text,
            food_name text,
            portion_type text,
            servings integer
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS foods (
            food_name text,
            portion_type text,
            calories integer
        )
    """)
    db_connection.commit()


def get_rows_from_table(db_connection, table_name:str, **match_criteria) -> list:
    """
    Retrieve all entries from specified table that fits the 
    match criteria.

    Match criteria should be passed as none or more kwargs in the 
    form: match_<column name>=<match criteria>, e.g:
        
        match_food_name='broccoli', match_portion_type='head'

    Always returns a list of none or more dictionaries, with each 
    dictionary containing the data of an individual row.
    """

    c = db_connection.cursor()

    match_string = db_convert_match_criteria_to_string(**match_criteria)
    # Supplying no match_criteria is a valid search, 
    # in that case we return the entire table.
    if match_string:
        match_string = 'WHERE ' + match_string

    c.execute(f"""
        SELECT *
        FROM {table_name}
        {match_string}
    """)
    rows = c.fetchall()

    output_list = []
    if table_name == 'foods':
        for row in rows:
            output_list.append({
                'food_name': row[0],
                'portion_type': row[1],
                'calories': row[2]
            })
    elif table_name == 'record':
        for row in rows:
            output_list.append({
                'date': parse_date_string_to_date_object(row[0]),
                'food_name': row[1],
                'portion_type': row[2],
                'servings': row[3]
            })
    
    return output_list


def add_row_to_table(db_connection, table_name:str,
    date:datetime=None, food_name:str=None, portion_type='', 
    servings=1, calories=0) -> None:
    """
    Adds input data to table specified by table_name argument.

    Desired input data should be passed as an appropriate kwarg
    for each separate column, e.g:

        food_name='broccoli'

    Not specifying data for a column will cause it to revert to
    a default value, this is desired behavior.
    
    Note: food_name is required to perform a sensible query. It is
    only listed as a keyword argument for the sake of consistency
    with the other functions.

    This function will not check whether or not a matching entry 
    is already present in the database.
    """
    # TODO P2 The last line of the docstring isn't true anymore, should it be?

    c = db_connection.cursor()
    
    if not food_name:
        print("add_rows_to_table(): no food_name given.")
        return 
    
    # Check whether the food already exists in the foods database.
    food_exists = get_rows_from_table(
        db_connection,
        'foods',
        match_food_name=food_name,
        match_portion_type=portion_type
    )

    if table_name == 'record':
        # # If the food doesn't exist in the foods db we prompt the user to add it first.
        # if not food_exists:
        # # TODO impliment this logic
            # print('food not in db')
            # return

        # Create datetime object at function call time.
        if date == None:
            date = datetime.now()
        
        # Check if an entry with the given food exists on the given day. 
        record_entries = get_rows_from_table(
            db_connection,
            'record', 
            match_date=date,
            match_food_name=food_name,
            match_portion_type=portion_type
        )
        # If it does, we increment the 'servings' variable and return.
        if record_entries:
            record_entry = record_entries[0]
            record_entry['servings'] += 1
            update_row_in_table(
                db_connection,
                'record',
                **record_entry, 
                match_date=date, 
                match_food_name=food_name,
                match_portion_type=portion_type
            )
            return
        # Else we simply add the entry to the record table.
        c.execute("""
            INSERT INTO record 
            VALUES (
                :date,
                :food_name,
                :portion_type,
                :servings
            )""",
            {
                'date': datetime.strftime(date, '%d-%m-%Y'),
                'food_name': food_name,
                'portion_type': portion_type,
                'servings': servings
            }
        )

    elif table_name == 'foods':
        if food_exists:
            print("add_row_to_table(): food already exists in database.")
            return

        c.execute("""
            INSERT INTO foods 
            VALUES (
                :food_name,
                :portion_type,
                :calories
            )""",
            {
                'food_name': food_name,
                'portion_type': portion_type,
                'calories': calories
            }
        )
    
    db_connection.commit()


def delete_rows_in_table(db_connection, table_name:str, **match_criteria) -> None:
    """
    Behaves similarly to get_rows_from_table() but deletes matching
    rows instead of returning them.
    """

    if not match_criteria:
        print("db.delete_rows_in_table: Warning, no match_criteria passed.")
        return
    
    c = db_connection.cursor()

    match_string = db_convert_match_criteria_to_string(**match_criteria)
    c.execute(f"""
        DELETE 
        FROM {table_name} 
        WHERE {match_string}
    """)

    db_connection.commit()


def delete_table(db_connection, table_name:str) -> None:
    """
    Delete given table.
    """

    c = db_connection.cursor()
    c.execute(f"""
        DROP 
        TABLE IF EXISTS {table_name}
    """)
    db_connection.commit()


def update_row_in_table(db_connection, table_name:str, **update_and_match_criteria) -> None:
    # TODO P4 audit docstring of db.update_row_in_table()
    """
    Replace columns of all rows that match the match criteria.

    Columns that should be updated should be passed as kwargs in the form
    <column name>=<new data>, e.g:

    Targeting specific rows to be updated is done by passing kwargs in
    the form match_<column name>=<match criteria>.

    An example usage of this function might look like this:

        update_row_in_table('foods', 
            match_food_name='broccoli', match_portion_type='head',
            calories=50
        )

    In this example case we update the calories value for a head of 
    broccoli in the foods table.
    """

    match_string = db_convert_match_criteria_to_string(**update_and_match_criteria)

    query_set_list = []
    for key in update_and_match_criteria:
        val = update_and_match_criteria[key]
        if not match('match_', key):
            if type(val) == str:
                query_set_list.append(f"{key} = '{val}'")
            elif type(val) == int:
                query_set_list.append(f"{key} = {val}")
            elif type(val) == datetime:
                query_set_list.append(datetime.strftime('%d-%m-%Y'))
    query_set_string = ', '.join(query_set_list)

    c = db_connection.cursor()
    if table_name == 'record':
        c.execute(f"""
            UPDATE record 
            SET {query_set_string}
            WHERE {match_string}
            """
        )
    elif table_name == 'foods':
        c.execute(f"""
            UPDATE foods 
            SET {query_set_string}
            WHERE {match_string}
            """
        )

    db_connection.commit()
