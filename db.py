# Functions for handling databases
# TODO add unit testing

import sqlite3
from datetime import datetime
import json

# We use 2 tables:
# 
# foods 
# Each row in the table represents a separate food item.
# Columns stored in the table are:
#   food_name: 
#       Self explanatory
#   portion_type: 
#       Each food has 1 or more associated portion types (glass, spoon, slice, etc).
#       Each portion type of a particular food is treated as a separate row in the table
#       but will be grouped together under the common food name when presented to the user.
#       Omitting a portion type is allowed on the user end, this will simply be treated as
#       it's own row where the portion type is an empty string
#   includes_foods: 
#       This acts sort of like an ingredients list which allows foods to be supersets
#       of other foods. each row in this list must be a list containing food name, 
#       portion type and number of servings of a food already present in the table
#       TODO make sure to prevent circular definitions
#       TODO make sure to take care of cases when food dependancies are deleted later
#   base_calories: 
#       When a food cannot be constructed purely as a superset of other foods
#       an integer of calories can be added. This is also useful for defining atomized foods
#
# record 
# Each row in the table represents one consumed food item. 
# Columns stored in the table are:
#   date: 
#       String in the form "dd-mm-yyyy"
#   food_name: 
#       String, corresponding to the same name as in the foods table
#   portion_type:
#       String, corresponding to the same name as in the foods table
#   servings:
#       Integer, number of items consumed
#       TODO increase this number when adding a new row of the same type on the same day, rather than adding a new row.


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


def add_row_to_table(db_path, table_name, input_data) -> None:
    """
    Adds input data to table specified by table_name argument.
    Data should be a dict with keys matching the database column names.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    if table_name == "record":
        c.execute("""
            INSERT INTO record 
            VALUES (
                :date,
                :food_name,
                :portion_type,
                :servings
            )""",
            {
                "date": input_data["date"],
                "food_name": input_data["food_name"],
                "portion_type": input_data["portion_type"],
                "servings": input_data["servings"]
            }
        )
    elif table_name == "foods":
        c.execute("""
            INSERT INTO foods 
            VALUES (
                :food_name,
                :portion_type,
                :includes_foods,
                :base_calories
            )""",
            {
                "food_name": input_data["food_name"],
                "portion_type": input_data["portion_type"],
                "includes_foods": json.dumps(input_data["includes_foods"]),
                "base_calories": input_data["base_calories"]
            }
        )
    conn.commit()
    conn.close()


def get_rows_from_table(db_path, table_name, **search_criteria) -> list:
    """
    Retrieve all entries from given table in given database that meet 
    the search criteria.
    Search criteria should be passed as none or more kwargs in the 
    form <column name>=<search value>".
    Always returns a list of none or more dictionaries representing 
    individual entries.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # construct the search criteria
    # consult sqlite documentation regarding the formatting
    condition_string = " AND ".join([f"{k} LIKE '%{v}%'" for k, v in search_criteria.items()])
    if condition_string:
        condition_string = "WHERE " + condition_string
    c.execute(f"""
        SELECT *
        FROM {table_name}
        {condition_string}
    """)
    rows = c.fetchall()
    conn.close()

    # parse data into a list of dictionaries
    output_list = []
    if table_name == "record":
        for row in rows:
            output_list.append({
                "date": row[0],
                "food_name": row[1],
                "portion_type": row[2],
                "servings": row[3]
            })
    elif table_name == "foods":
        for row in rows:
            # this is stored as a string of json data in the table, we need to parse it first
            output_list.append({
                "food_name": row[0],
                "portion_type": row[1],
                "includes_foods": json.loads(row[2]),
                "base_calories": row[3]
            })
    return output_list


# def update_table(db_path, table_name, input_data) -> None:
#     """Updates a row in the record database with given json data"""
#     parsed_data = parse_json_string("record", data_json_string)
#     conn = sqlite3.connect(record_db_path)
#     c = conn.cursor()
#     c.execute("""
#         UPDATE record SET
#             date = :date,
#             food_name = :food_name,
#             portion_type = :portion_type,
#             servings = :servings
#     
#         WHERE date=:date AND food_name=:food_name AND portion_type=:portion_type""",
#         {
#             "date": parsed_data["date"],
#             "food_name": parsed_data["food_name"],
#             "portion_type": parsed_data["portion_type"],
#             "servings": parsed_data["servings"]
#         }
#     )
#     conn.commit()
#     conn.close()


# def update_foods_db(data_json_string) -> None:
#     """Updates a row in the foods database with given json data"""
#     parsed_data = parse_json_string("foods", data_json_string)
#     conn = sqlite3.connect(record_db_path)
#     c = conn.cursor()
#     c.execute("""
#         UPDATE foods SET 
#             food_name = :text,
#             portion_type = :text,
#             includes_foods = :text,
#             base_calories = :integer
#     
#         WHERE food_name=:food_name AND portion_type=:portion_type""",
#         {
#             "food_name": parsed_data["food_name"],
#             "portion_typ": parsed_data["portion_type"],
#             "includes_foods": parsed_data["includes_foods"],
#             "base_calories": parsed_data["base_calories"]
#         }
#     )
#     conn.commit()
#     conn.close()
    
                
def delete_rows_in_table(db_path, table_name, **search_criteria) -> None:
    """
    Behaves similarly to get_rows_from_table but deletes
    matching search criteria instead.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # construct the search criteria
    # consult sqlite documentation regarding the formatting
    condition_string = " AND ".join([f"{k} LIKE '%{v}%'" for k, v in search_criteria.items()])
    if condition_string:
        c.execute(f"""
            DELETE 
            FROM {table_name} 
            WHERE {condition_string}
        """)
    conn.close()


def delete_table(db_path, table_name):
    """
    Delete given table in given database
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f"""
        DROP 
        TABLE IF EXISTS {table_name}
    """)
