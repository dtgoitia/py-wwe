import requests
import datetime

UKGOV_TIMESTAMP_FORMAT = '%Y-%m-%d'


def gov_uk_bank_holidays() -> set:
    """Fetch bank holiday list for England from the UK government endpoint."""
    url = 'https://www.gov.uk/bank-holidays.json'
    r = requests.get(url)
    data = r.json()
    england_data = data['england-and-wales']['events']
    for event in england_data:
        date = datetime.datetime.strptime(event['date'], UKGOV_TIMESTAMP_FORMAT)
        yield date


def gov_uk_bank_holidays_between(start: datetime.datetime, end: datetime.datetime) -> set:
    """Filter bank holidays between two given dates."""
    return [day for day in gov_uk_bank_holidays() if start <= day <= end]
