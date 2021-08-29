"""
Utility functions used by various other functions in the code
"""
# TODO replace all datetime objects with date objects
from datetime import date
import re


def db_convert_match_criteria_to_string(**match_criteria) -> str:
    """
    Takes criteria that should match a row in the database and constructs
    a string that is correctly formatted for an sqlite query.

    Match criteria should be passed as none or more kwargs in the 
    form: match_<column name>=<search value>, e.g:
        
        match_food_name='broccoli', match_portion_type='head'
    """

    if match_criteria.get('match_date'):
        match_criteria['match_date'] = date.strftime(match_criteria['match_date'], '%d-%m-%Y')

    REMOVE_PREFIX = re.compile(r'^match_')
    match_string = ' AND '.join([
        f"{REMOVE_PREFIX.sub('', key)} LIKE '%{value}%'" 
        for key, value in match_criteria.items() 
        if bool(re.match('match_', key))
    ])
    return match_string
    

def parse_date_string_to_date_object(date_string):
    """
    Converts a string of the form "DD-MM-YYYY" or 'DDMMYYYY' (adding the year
    is optional) to a valid date object.

    Converting back can simply be done with the datetime.strftime() method.
    """

    valid_date = r'^([\d]{1,2})-?([\d]{1,2})-?([\d]{4})?$'
    match = re.match(valid_date, date_string)
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year = match.group(3)
        if year:
            year = int(year)
        else:
            year = date.today().year
        return date(year, month, day)
    raise Exception('Could not parse date from string.')
