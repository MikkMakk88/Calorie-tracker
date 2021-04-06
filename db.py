# Functions for handling databases

import sqlite3
from datetime import datetime
import json

# We use 2 different databases,
# one for storing food names long with price per x,
# another for storing a record of entries
record_db_path = "record.db"
foods_db_path = "foods.db"


def create_databases():
    """Creates the two empty databases.
    This function probably only needs to be run once."""

    conn = sqlite3.connect(record_db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE record (
            date text,
            food text,
            portion_type text,
            servings integer,
            calories integer,
            total integer
        )
    """)
    conn.commit()
    conn.close()

    conn = sqlite3.connect(foods_db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE foods (
            food text,
            portion_types,
            calories
        )
    """)
    conn.commit()
    conn.close()


def update_db(db, data) -> int: 
    """Updates specified database with given json data.
    Returns a completion code 1 for success, 0 for failure."""
    
    # set path
    if db == "record":
        path = record_db_path
    elif db == "foods":
        path = foods_db_path
    else:
        return 0

    # check validity of data
    

# utility functions
def string_to_list(json_str) -> list:
    json_str = json_str.strip('[]')
    parsed_l = json_str.split(', ')
    return parsed_l


def list_to_string(json_l) -> str:
    pass