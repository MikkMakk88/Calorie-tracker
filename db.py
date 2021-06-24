# Functions for handling databases

import sqlite3
from datetime import datetime
import json

# We use 2 different databases:
# 
# foods database
# Each entry in the database represents a separate food item.
# Columns stored in the databse are:
#   food_name: 
#       Self explanatory
#   portion_type: 
#       Each food has 1 or more associate portion type(glass, spoon, slice, etc).
#       Each portion type of a particular food is treated as a separate entry in the database
#       but will be grouped together under the common food name when presented to the user.
#       Omitting a portion type is allowed on the user end, this will simply be treated as
#       it's own entry in the database where the portion type is an empty string
#   includes_foods: 
#       This acts sort of like an ingredients list which allows foods to be supersets
#       of other foods. each entry in this list must be a list containing both food name and 
#       portion type.
#       TODO make sure to prevent circular definitions
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
#       TODO increase this number when adding a new entry of the same type on the same day,
#       rather than adding a new entry.
# 
# The databases store data as json strings


record_db_path = "record.db"
foods_db_path = "foods.db"


def create_databases() -> int:
    """Creates the two empty databases.
    This function probably only needs to be run once.
    Returns 1 on success, 0 on failure"""

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


def add_entry_record_db(data_json_string) -> None:
    """Adds given json data to record database"""
    pass


def add_entry_foods_db(data_json_string) -> None:
    """Adds given json data to foods database"""
    pass


def update_record_db(data_json_string) -> None:
    """Updates an entry in the record database with given json data"""
    
    parsed_data = parse_and_verify_data(data_json_string)

    conn = sqlite.connect(record_db_path)
    c = conn.cursor()
    c.execute("""
        UPDATE record SET
            date = :date,
            food_name = :food_name,
            portion_type = :portion_type,
            servings = :servings
    
        WHERE date=:date AND food_name=:food_name AND portion_type=:portion_type""",
        {
            "date": parsed_data["date"],
            "food_name": parsed_data["food_name"],
            "portion_type": parsed_data["portion_type"],
            "servings": parsed_data["servings"]
        }
    )
    conn.commit()
    conn.close()


def update_foods_db(data_json_string) -> None:
    """Updates an entry in the foods database with given json data"""
    parsed_data = parse_and_verify_data(data_json_string)

    conn = sqlite3.connect(record_db_path)
    c = conn.cursor()
    c.execute("""
        UPDATE foods SET 
            food_name = :text,
            portion_type = :text,
            includes_foods = :text,
            base_calories = :integer
    
        WHERE food_name=:food_name AND portion_type=:portion_type""",
        {
            "food_name": parsed_data["food_name"],
            "portion_typ": parsed_data["portion_type"],
            "includes_foods": parsed_data["includes_foods"],
            "base_calories": parsed_data["base_calories"]
        }
    )
    conn.commit()
    conn.close()
    
                
def parse_and_verify_data(db_name, parsed_data) -> int:
    """"""
    return None    

