"""
Low-level functions for directly handling the database.

"""
import sqlite3
from datetime import datetime
from json import dumps, loads

from utilities import db_convert_match_criteria_to_string

# TODO make sure to prevent circular definitions in the foods database.
# TODO make sure to take care of cases when food dependancies are deleted later.


def create_db_and_tables(db_path) -> None:
    """
    Creates the database with the two separate tables.

    This function probably only needs to be run once.
    """

    conn = sqlite3.connect(db_path)
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
            includes_foods text,
            base_calories integer
        )
    """)
    conn.commit()
    conn.close()


def add_row_to_table(db_path, table_name, new_data) -> None:
    """
    Adds input data to table specified by table_name argument.

    Data should be a dict with keys matching the database column names.
    """

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    if table_name == 'record':
        c.execute("""
            INSERT INTO record 
            VALUES (
                :date,
                :food_name,
                :portion_type,
                :servings
            )""",
            {
                'date': new_data['date'],
                'food_name': new_data['food_name'],
                'portion_type': new_data['portion_type'],
                'servings': new_data['servings']
            }
        )
    elif table_name == 'foods':
        c.execute("""
            INSERT INTO foods 
            VALUES (
                :food_name,
                :portion_type,
                :includes_foods,
                :base_calories
            )""",
            {
                'food_name': new_data['food_name'],
                'portion_type': new_data['portion_type'],
                'includes_foods': dumps(new_data['includes_foods']),
                'base_calories': new_data['base_calories']
            }
        )
    conn.commit()
    conn.close()


def get_rows_from_table(db_path, table_name, **match_criteria) -> list:
    """
    Retrieve all entries from given table in given database that meet 
    the search criteria.

    Search criteria should be passed as none or more kwargs in the 
    form <column name>=<search value>.

    Always returns a list of none or more dictionaries representing 
    individual entries.
    """

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    match_string = db_convert_match_criteria_to_string(**match_criteria)
    # Supplying no match_critera is a valid search, 
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
    if table_name == 'record':
        for row in rows:
            output_list.append({
                'date': row[0],
                'food_name': row[1],
                'portion_type': row[2],
                'servings': row[3]
            })
    elif table_name == 'foods':
        for row in rows:
            # this is stored as a string of json data in the table,
            # we need to parse it first.
            output_list.append({
                'food_name': row[0],
                'portion_type': row[1],
                'includes_foods': loads(row[2]),
                'base_calories': row[3]
            })
    return output_list


def delete_rows_in_table(db_path, table_name, **match_criteria) -> None:
    """
    Behaves similarly to get_rows_from_table but deletes matching
    criteria instead.
    """

    if not match_criteria:
        print("db.delete_rows_in_table: Warning, no match_critera passed.")
        return
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # construct the search criteria.
    # consult sqlite documentation regarding the formatting.
    match_string = db_convert_match_criteria_to_string(**match_criteria)
    c.execute(f"""
        DELETE 
        FROM {table_name} 
        WHERE {match_string}
    """)
    conn.commit()
    conn.close()


def delete_table(db_path, table_name) -> None:
    """
    Delete given table in given database
    """

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f"""
        DROP 
        TABLE IF EXISTS {table_name}
    """)


def update_row_in_table(db_path, table_name, 
                        new_data, **match_criteria) -> None:
    """
    In given database, replace row that matches match_criteria with new_data.

    As with get_rows_from_table(), match criteria should be passed as 
    none or more kwargs in the form <column name>=<match value>. 
    """

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    match_string = db_convert_match_criteria_to_string(**match_criteria)
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
                'date': new_data['date'],
                'food_name': new_data['food_name'],
                'portion_type': new_data['portion_type'],
                'servings': new_data['servings']
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
                'food_name': new_data['food_name'],
                'portion_type': new_data['portion_type'],
                'includes_foods': dumps(new_data['includes_foods']),
                'base_calories': new_data['base_calories']
            }
        )
    conn.commit()
    conn.close()
