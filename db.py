"""
Low-level functions for directly handling the database.
"""
import sqlite3
from datetime import datetime
from json import dumps, loads

from utilities import db_convert_match_criteria_to_string
import cfg

# TODO make sure to prevent circular definitions in the foods database.
# TODO make sure to take care of cases when food dependancies are deleted later.
# TODO review docstrings in db.py


def create_db_and_tables() -> None:
    """
    Creates the database with the two separate tables.

    This function probably only needs to be run once.
    """

    conn = sqlite3.connect(cfg.db_path)
    c = conn.cursor()
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
    conn.commit()
    conn.close()


def get_rows_from_table(table_name:str, **match_criteria) -> list:
    """
    Retrieve all entries from specified table that meets the 
    match criteria.

    Match criteria should be passed as none or more kwargs in the 
    form: match_<column name>=<match criteria>, e.g:
        
        match_food_name='broccoli', match_portion_type='head'

    Always returns a list of none or more dictionaries, with each 
    dictionary containing the data of an individual row.
    """

    conn = sqlite3.connect(cfg.db_path)
    c = conn.cursor()

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
    conn.close()

    # Parse data into a list of dictionaries.
    output_list = []
    if table_name == 'foods':
        for row in rows:
            output_list.append({
                'food_name': row[0],
                'portion_type': row[1],
                'calories': row[3]
            })
    elif table_name == 'record':
        for row in rows:
            output_list.append({
                'date': row[0],
                'food_name': row[1],
                'portion_type': row[2],
                'servings': row[3]
            })
    
    return output_list


def add_row_to_table(table_name:str,
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

    conn = sqlite3.connect(cfg.db_path)
    c = conn.cursor()
    
    if not food_name:
        print("add_rows_to_table(): no food_name given.")
        return 
    
    # Check whether the food already exists in the foods database.
    food_exists = get_rows_from_table(
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
        date_str = datetime.strftime(date, '%d-%m-%Y')
        
        # Check if an entry with the given food exists on the given day. 
        record_entries = get_rows_from_table(
            'record', 
            match_date=date_str,
            match_food_name=food_name,
            match_portion_type=portion_type
        )
        # If it does, we increment the 'servings' variable and return.
        if record_entries:
            record_entry = record_entries[0]
            record_entry['servings'] += 1
            update_row_in_table(
                'record',
                **record_entry, 
                match_date=date_str, 
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
                'date': date_str,
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
    
    conn.commit()
    conn.close()


def delete_rows_in_table(table_name:str, **match_criteria) -> None:
    """
    Behaves similarly to get_rows_from_table() but deletes matching
    rows instead of returning them.
    """

    if not match_criteria:
        print("db.delete_rows_in_table: Warning, no match_criteria passed.")
        return
    
    conn = sqlite3.connect(cfg.db_path)
    c = conn.cursor()

    match_string = db_convert_match_criteria_to_string(**match_criteria)
    c.execute(f"""
        DELETE 
        FROM {table_name} 
        WHERE {match_string}
    """)

    conn.commit()
    conn.close()


def delete_table(table_name:str) -> None:
    """
    Delete given table.
    """

    conn = sqlite3.connect(cfg.db_path)
    c = conn.cursor()
    c.execute(f"""
        DROP 
        TABLE IF EXISTS {table_name}
    """)
    conn.commit()
    conn.close()


def update_row_in_table(table_name:str, **update_and_match_criteria) -> None:
    # TODO audit docstring of db.update_row_in_table()
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

    conn = sqlite3.connect(cfg.db_path)
    c = conn.cursor()

    match_string = db_convert_match_criteria_to_string(**update_and_match_criteria)
    if table_name == 'record':
        c.execute(f"""
            UPDATE record 
            SET date = :date,
                food_name = :food_name,
                portion_type = :portion_type,
                servings = :servings
    
            WHERE {match_string}
            """,
            {
                'date': update_and_match_criteria['date'],
                'food_name': update_and_match_criteria['food_name'],
                'portion_type': update_and_match_criteria['portion_type'],
                'servings': update_and_match_criteria['servings']
            }
        )
    elif table_name == 'foods':
        c.execute(f"""
            UPDATE foods 
            SET date = :date,
                food_name = :food_name,
                portion_type = :portion_type,
                servings = :servings
    
            WHERE {match_string}
            """,
            {
                'food_name': update_and_match_criteria['food_name'],
                'portion_type': update_and_match_criteria['portion_type'],
                'calories': update_and_match_criteria['calories']
            }
        )

    conn.commit()
    conn.close()
