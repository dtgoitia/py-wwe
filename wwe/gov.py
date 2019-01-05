import click
import datetime
import requests
import wwe.log as log

UKGOV_TIMESTAMP_FORMAT = '%Y-%m-%d'


def gov_uk_bank_holidays() -> set:
    """Fetch bank holiday list for England from the UK government endpoint."""
    if log.verbose:
        click.echo('Fetching bank holidays from UK Government API...')
    r = requests.get('https://www.gov.uk/bank-holidays.json')
    data = r.json()
    england_data = data['england-and-wales']['events']
    for event in england_data:
        date = datetime.datetime.strptime(event['date'], UKGOV_TIMESTAMP_FORMAT)
        yield date


def gov_uk_bank_holidays_between(start: datetime.datetime, end: datetime.datetime) -> int:
    """Return the total amount of bank holidays between two given dates."""
    bank_holidays = [day for day in gov_uk_bank_holidays() if start <= day <= end]
    return len(bank_holidays)
