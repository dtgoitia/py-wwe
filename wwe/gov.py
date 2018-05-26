import requests
import datetime

UKGOV_TIMESTAMP_FORMAT = '%Y-%m-%d'


def gov_uk_bank_holidays() -> set:
    """
    Fetch bank holiday list for England from the UK government endpoint
    """
    url = 'https://www.gov.uk/bank-holidays.json'
    r = requests.get(url)
    data = r.json()
    england_data = data['england-and-wales']
    events = england_data['events']
    result = set()
    for event in events:
        date_str = event.get('date')
        date = datetime.datetime.strptime(date_str, UKGOV_TIMESTAMP_FORMAT)
        result.add(date)
    return result


def gov_uk_bank_holidays_between(start: datetime.datetime, end: datetime.datetime) -> set:
    """
    Filter bank holidays between two given dates
    """
    bank_holidays = gov_uk_bank_holidays()
    result = set()
    for day in bank_holidays:
        if start <= day and day <= end:
            result.add(day)
    return result
