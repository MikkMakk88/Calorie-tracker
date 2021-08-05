"""
Functions to process operations that should be performed on the database.
"""
from datetime import datetime

import db
import cfg


def add_food_to_record(date:datetime, food_name, portion_type, servings):
    """
    This function is called whenever we want to add a consumed food to the 
    record database.
    """
    date_str = datetime.strftime(date, '%d-%m-%Y')
    
    # Check if an entry with the same food exists on that day 
    # If true then we increment the "servings" variable and return
    record_entries = db.get_rows_from_table(
        cfg.db_path,
        'record', 
        date=date_str,
        food_name=food_name
    )
    if record_entries:
       # TODO: update_row with new serving count 
       pass

    # TODO if the food doesn't exist in the food db we prompt the user to add it first

    # We then assemble the data and add the entry to the record
    input_data = {
        "date": date_str,
        "food_name": food_name,
        "portion_type": portion_type,
        "servings": servings
    }
    db.add_row_to_table(
        cfg.db_path,
        'record',
        input_data
    )
