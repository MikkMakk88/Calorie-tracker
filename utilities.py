"""
Utility functions used by various other functions in the code

"""
from datetime import datetime
from json import dumps
import re


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

    Match criteria should be passed as none or more kwargs in the 
    form: match_<column name>=<search value>, e.g:
        
        match_food_name='broccoli', match_portion_type='head'
    """

    if match_criteria.get('match_includes_foods'):
        match_criteria['match_includes_foods'] = dumps(match_criteria['match_includes_foods'])

    # remove preceeding 'match_' from each key in the dict and construct the 
    # query string.
    REMOVE_PREFIX = re.compile(r'^match_')
    match_string = ' AND '.join([
        f"{REMOVE_PREFIX.sub('', key)} LIKE '%{value}%'" 
        for key, value in match_criteria.items() 
        if bool(re.match('match_', key))
        ])
    return match_string
    