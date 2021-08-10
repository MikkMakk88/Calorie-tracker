"""
Utility functions used by various other functions in the code
"""
from datetime import datetime
from json import dumps


def convert_date_str_to_datetime(date_str) -> datetime:
    """
    Converts a string of the form "dd-mm-yyyy" to a valid datetime object.
    Converting back can simply be done with the datetime.strftime() method.
    """
    values = date_str.split('-')
    d = int(values[0])
    m = int(values[1])
    y = int(values[2])
    return datetime(y, m, d)


def db_convert_match_criteria_to_string(**match_criteria) -> str:
    """
    Takes criteria that should match a row in the database and constructs
    a string that is correctly formatted for an sqlite query.
    arguments should be any number of kwargs in the form 
    <column name>=<search value>.
    """
    if match_criteria.get('includes_foods'):
        match_criteria['includes_foods'] = dumps(match_criteria['includes_foods'])
    # construct the search criteria
    # consult sqlite documentation regarding the formatting
    condition_string = ' AND '.join([f"{k} LIKE '%{v}%'" for k, v in match_criteria.items()])
    return condition_string
    