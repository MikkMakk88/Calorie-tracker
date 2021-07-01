# Functions for handling databases
# TODO add unit testing

import sqlite3
from datetime import datetime
import json
import os

# We use 2 different databases:
# 
# foods database
# Each entry in the database represents a separate food item.
# Columns stored in the databse are:
#   food_name: 
#       Self explanatory
#   portion_type: 
#       Each food has 1 or more associated portion types (glass, spoon, slice, etc).
#       Each portion type of a particular food is treated as a separate entry in the database
#       but will be grouped together under the common food name when presented to the user.
#       Omitting a portion type is allowed on the user end, this will simply be treated as
#       it's own entry in the database where the portion type is an empty string
#   includes_foods: 
#       This acts sort of like an ingredients list which allows foods to be supersets
#       of other foods. each entry in this list must be a list containing food name, 
#       portion type and number of servings of a food already present in this database
#       TODO make sure to prevent circular definitions
#       TODO make sure to take care of cases when food dependancies are deleted later
#   base_calories: 
#       When a food cannot be constructed purely as a superset of other foods
#       an integer of calories can be added. This is also useful for defining atomized foods
#
# record database
# Each entry in the database represents one consumed food item. 
# Columns stored in the database are:
#   date: 
#       String in the form "dd-mm-yyyy"
#   food_name: 
#       String, corresponding to the same name as in the foods database
#   portion_type:
#       String, corresponding to the same name as in the foods database
#   servings:
#       Integer, number of items consumed
#       TODO increase this number when adding a new entry of the same type on the same day, rather than adding a new entry.
# 
# The databases store data as json strings

record_db_path = "record.db"
foods_db_path = "foods.db"

def create_databases() -> None:
    """Creates the two empty databases.
    This function probably only needs to be run once.
    """
    conn = sqlite3.connect(record_db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE record (
            date text,
            food_name text,
            portion_type text,
            servings integer
        )
    """)
    conn.commit()
    conn.close()

    conn = sqlite3.connect(foods_db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE foods (
            food_name text,
            portion_type text,
            includes_foods text,
            base_calories integer
        )
    """)
    conn.commit()
    conn.close()


def add_entry_record_db(input_data) -> None:
    """Adds given data to record database
    Data should be a dict with keys matching the database column names"""
    conn = sqlite3.connect(record_db_path)
    c = conn.cursor()
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
    conn.commit()
    conn.close()


def add_entry_foods_db(input_data) -> None:
    """Adds given data to foods database
    Data should be a dict with keys matching the database column names
    includes_foods should be a list of lists"""
    conn = sqlite3.connect(foods_db_path)
    c = conn.cursor()
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


def get_entry_from_db(db_name, **search_criteria) -> list:
    """Retrieve all entries from given database that meet the search criteria.
    Search criteria should be passed as kwargs in the form <column name>=<search value>"
    Always returns a list of none or more dictionaries representing individual entires"""

    # connect to correct database    
    if db_name == "record":
        conn = sqlite3.connect(record_db_path)
    else:
        conn = sqlite3.connect(foods_db_path)
    c = conn.cursor()
    
    # construct the search criteria
    # consult sqlite documentation regarding the formatting
    condition_string = " AND ".join([f"{k} LIKE '%{v}%'" for k, v in search_criteria.items()])
    if condition_string:
        condition_string = "WHERE " + condition_string
    c.execute(f"""
        SELECT *
        FROM {db_name}
        {condition_string}
    """)
    entries = c.fetchall()
    conn.close()

    # parse data into a list of dictionaries
    output_list = []
    if db_name == "record":
        for entry in entries:
            output_list.append({
                "date": entry[0],
                "food_name": entry[1],
                "portion_type": entry[2],
                "servings": entry[3]
            })
    else:
        for entry in entries:
            # this is stored as a string of json data in the db, we need to parse it first
            output_list.append({
                "food_name": entry[0],
                "portion_type": entry[1],
                "includes_foods": json.loads(entry[2]),
                "base_calories": entry[3]
            })
    return output_list


def update_record_db(data_json_string) -> None:
    # """Updates an entry in the record database with given json data"""
    # parsed_data = parse_json_string("record", data_json_string)
    # conn = sqlite3.connect(record_db_path)
    # c = conn.cursor()
    # c.execute("""
    #     UPDATE record SET
    #         date = :date,
    #         food_name = :food_name,
    #         portion_type = :portion_type,
    #         servings = :servings
    
    #     WHERE date=:date AND food_name=:food_name AND portion_type=:portion_type""",
    #     {
    #         "date": parsed_data["date"],
    #         "food_name": parsed_data["food_name"],
    #         "portion_type": parsed_data["portion_type"],
    #         "servings": parsed_data["servings"]
    #     }
    # )
    # conn.commit()
    # conn.close()
    pass


def update_foods_db(data_json_string) -> None:
    # """Updates an entry in the foods database with given json data"""
    # parsed_data = parse_json_string("foods", data_json_string)
    # conn = sqlite3.connect(record_db_path)
    # c = conn.cursor()
    # c.execute("""
    #     UPDATE foods SET 
    #         food_name = :text,
    #         portion_type = :text,
    #         includes_foods = :text,
    #         base_calories = :integer
    
    #     WHERE food_name=:food_name AND portion_type=:portion_type""",
    #     {
    #         "food_name": parsed_data["food_name"],
    #         "portion_typ": parsed_data["portion_type"],
    #         "includes_foods": parsed_data["includes_foods"],
    #         "base_calories": parsed_data["base_calories"]
    #     }
    # )
    # conn.commit()
    # conn.close()
    pass
    
                
def debug_get_all_entries(print=False):
    # retrieve entries from record database
    conn = sqlite3.connect(record_db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM record")
    record_entries = c.fetchall()

    # retrieve entries from foods database    
    conn = sqlite3.connect(foods_db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM foods")
    foods_entries = c.fetchall()
    
    # print them out
    if print:
        print("record:")
        for entry in record_entries:
            print("    ", entry)
        print("foods:")
        for entry in foods_entries:
            print("    ", entry)
        conn.close()

    # return them
    return (record_entries, foods_entries)


def delete_databases():
    if os.path.exists("record.db"):
        os.remove("record.db")
    if os.path.exists("foods.db"):
        os.remove("foods.db")
