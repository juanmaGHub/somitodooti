from dateutil.parser import parse
from datetime import datetime


# Date Utils
def str2utc(date):
    """
        Transform virtually any str date format to unix timestamp
        params: date string
    """
    try:
        date = parse(date)
    except ValueError:
        return False
    return date

def unix2utc(date):
    """
        Transform unix timestamp to readable date 
        params: date timestamp
    """
    try:
        date = datetime.fromtimestamp(int(date))
    except ValueError:
        return False
    return date

def parse_dates(date):
    """
        Parse date to unix timestamp
        params: date
    """
    # Check if date is empty
    if not date:
        return False
    
    # Check if date is already a datetime object
    if isinstance(date, datetime):
        return date
    
    # Try to parse date by any means possible
    if isinstance(date, str):
        parsed_date = str2utc(date)
        # Check if date was already a timestamp
        if not parsed_date:
            parsed_date = unix2utc(date)
    elif isinstance(date, int):
        parsed_date = unix2utc(date)
    else:
        return False
    
    return parsed_date
