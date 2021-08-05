"""
Utility functions used by various other functions in the code
"""

from datetime import datetime

def convert_date_str_to_datetime(date_str) -> str:
    """
    Converts a string of the form "dd-mm-yyyy" to a valid datetime object.
    Converting back can simply be done with the datetime.strftime() method.
    """
    values = date_str.split('-')
    d = int(values[0])
    m = int(values[1])
    y = int(values[2])
    return datetime(y, m, d)

