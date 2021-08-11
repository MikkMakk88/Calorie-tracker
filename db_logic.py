"""
Functions to handle slightly more complex operations that should be performed 
on the database.

"""
from datetime import datetime
import db, cfg


def add_food_to_foods_table(food_name, portion_type='', 
                            includes_foods=None, base_calories=0) -> None:
    """
    This acts mostly as a wrapper for db.add_row_to_table(), added for 
    the sake of consistency.

    This function will not check whether the food already exists in the table.
    """

    # avoid creating a shared mutable type when defining the function
    if includes_foods == None:
        includes_foods = []

    new_data = {
        'food_name': food_name,
        'portion_type': portion_type,
        'includes_foods': includes_foods,
        'base_calires': base_calories
    }
    db.add_row_to_table(cfg.db_path, 'foods', new_data)


def add_entry_to_record_table(food_name, date=None, 
                              portion_type='', servings=1) -> None:
    """
    Makes multiple queries to the database and performs logic to correctly 
    process requests to add a food entry to the record table.
    """

    # Check whether the food and portion_type exists in the foods database or 
    # not. If not, then we prompt the user to add it first.
    food_entries = db.get_rows_from_table(
        cfg.db_path, 
        'foods',
        food_name=food_name,
        portion_type=portion_type
    )
    if food_entries:
        food_entry = food_entries[0]
    else:
    # TODO if the food doesn't exist in the food db we prompt the user to add it first
        print('food not in db')
        return

    if date == None:
        date = datetime.now()
    date_str = datetime.strftime(date, '%d-%m-%Y')

    # Check if an entry with the given food exists on the given day. 
    record_entries = db.get_rows_from_table(
        cfg.db_path,
        'record', 
        date=date_str,
        food_name=food_name,
        portion_type=portion_type
    )
    # If true then we increment the 'servings' variable and return.
    if record_entries:
        record_entry = record_entries[0]
        record_entry['servings'] += 1
        db.update_row_in_table(
            cfg.db_path, 
            'record',
            record_entry, 
            date=date_str, 
            food_name=food_name,
            portion_type=portion_type
        )
        return
    # Else we assemble the data and add the entry to the record.
    new_data = {
        'date': date_str,
        'food_name': food_name,
        'portion_type': portion_type,
        'servings': servings
    }
    db.add_row_to_table(
        cfg.db_path,
        'record',
        new_data
    )
