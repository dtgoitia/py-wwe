import click
from colorama import init, Fore, Style
import datetime
import functools
from typing import List
from wwe.toggl import TogglWrap
from wwe.config import load_config
from wwe.gov import gov_uk_bank_holidays_between
import wwe.log as log
from wwe.log import set_verbose_mode


# (start, end)
# (00:00:00, 23:59:59)
# (08:30:00, 16:00:00)

def partition_days_between(start_date: datetime.datetime, end_date: datetime.datetime):
    """Generate a stream of tuples with two datetimes that run from the start_date to the end_date.

    Input> 2000-01-01 12:34:56 - 2000-01-03 19:00:19
    Would generate:
    (2000-01-01 12:34:56, 2000-01-01 23:59:59)
    (2000-01-02 00:00:00, 2000-01-02 23:59:59)
    (2000-01-03 00:00:00, 2000-01-03 19:00:19)
    """
    current_ts = start_date
    while current_ts < end_date:
        last_time_today = current_ts.replace(hour=23, minute=59, second=59)
        yield (current_ts, last_time_today)
        current_ts = last_time_today + datetime.timedelta(seconds=1)


def filter_out_weekends(times):
    """Filter out Saturday and Sunday."""
    for start, end in times:
        if start.weekday() < 5:
            yield (start, end)


def filter_out_non_working_hours(times):  # TODO: what's this?
    """Filter out non-working hours."""
    for start, end in times:
        pass


def get_project_ids(target_client: str, t: TogglWrap) -> set:
    """Return all project IDs accross all workspaces for a given client.

    Args:
        target_client (str): name of the client from whom to get the projects.
        t (TogglWrap): Toggl client wrapper.
    """
    work_projects = set()
    for workspace in t.toggl.get_workspaces():
        workspace_id = workspace['id']
        clients = t.toggl.get_clients(workspace_id=workspace_id)
        projects = t.toggl.get_projects(workspace_id=workspace_id)
        for client in clients:
            client_name = client['name']
            if target_client != client_name:
                continue
            client_id = client['id']
            for project in projects:
                project_client = project.get('cid')
                if project_client != client_id:
                    continue
                work_projects.add(project['id'])
    return work_projects


def is_work(entry: dict, work_projects: List[str]):
    """Return true if the entrie belongs to any of the work_projects."""
    if entry['pid'] in work_projects:
        return True
    return False


def get_weekend_days_between(start: datetime.datetime, end: datetime.datetime) -> int:
    """Return the number of weekend days between two given dates."""
    result = 0
    current_date = start
    while current_date < end:
        if current_date.weekday() > 4:
            result += 1
        current_date += datetime.timedelta(days=1)
    return result


def get_holiday_amount(days: any, start: datetime.datetime, end: datetime.datetime) -> float:
    """Return the number of holidays between two given dates.

    Any dates later than the current date are ignored, as they
    represent booked annual leaves for the future.

    Example of 'day' argument values: ["2018-11-07", 1], ["2018-11-08", 0.5]...

    :param days: list of tuples, as shown above
    :param start: date from which to start counting (included)
    :param end: last date to be included in the count
    :returns: number of personal holidays
    """
    result = 0
    for day in days:
        current_day = datetime.datetime.strptime(day[0], '%Y-%m-%d')
        if start <= current_day <= end:
            result += float(day[1])
    return result


def get_personal_holidays_between(config: any, start: datetime.datetime, end: datetime.datetime) -> float:
    """Return the number of days off booked by a person between two given dates."""
    if log.verbose:
        click.echo('Loading personal holidays from configuration file...')
    personal_holidays = config['personal_holidays']
    return get_holiday_amount(personal_holidays, start, end)


def get_company_holidays_between(config: any, start: datetime.datetime, end: datetime.datetime) -> float:
    """Return the number of extra days off a by a person between two given dates."""
    if log.verbose:
        click.echo('Loading company holidays from configuration file...')
    return get_holiday_amount(config['company_bonus_days'], start, end)


def format_balance(delta: datetime.timedelta) -> str:
    """Return a formated string with the time delta.

    Remove the microseconds from the time delta and only show the required
    time units.
    """
    days = delta.days
    secs = delta.seconds
    hours, remainder = divmod(secs, 3600)
    minutes, seconds = divmod(remainder, 60)

    formatted_chunks = ()
    if days:
        formatted_chunks += (f'{days}d', )
    if hours:
        formatted_chunks += (f'{hours}h', )
    if minutes:
        formatted_chunks += (f'{minutes}min',)
    result = ', '.join(formatted_chunks)

    return result


def print_balance(to_work: datetime.datetime, worked: datetime.datetime):
    """Format balance and print it on screen.

    This function considers whether the balance is positive or negative, and format it consequently.
    """
    if to_work > worked:
        balance = format_balance(to_work - worked)
        coloured_balance = Fore.RED + balance + Style.RESET_ALL
        click.echo(f"You need to work {coloured_balance} more today")
    else:
        balance = format_balance(worked - to_work)
        coloured_balance = Fore.GREEN + balance + Style.RESET_ALL
        click.echo(f"You have worked {coloured_balance} extra so far")


@click.command()
@click.option('--verbose', '-v', is_flag=True, default=False, help='Enable logging')
def main(verbose):
    """Run main function."""
    set_verbose_mode(verbose)
    init()  # initialize colorama package
    config = load_config()
    start = datetime.datetime.strptime(config['client']['start_date'], '%Y-%m-%d')
    t = TogglWrap(token=config['toggl_token'])
    project_ids = get_project_ids(target_client=config['client']['name'], t=t)
    filters = [functools.partial(is_work, work_projects=project_ids)]

    worked = datetime.timedelta()
    for entry in t.get_filtered_entries(filters=filters, start=start):
        duration = entry['duration']

        # unfinished time entries have negative durations
        if duration.days < 0:
            tz = entry['start'].tzinfo
            now = datetime.datetime.now(tz)
            duration = now - entry['start']
        worked += duration

    now = datetime.datetime.now()
    bank_holidays = gov_uk_bank_holidays_between(start, now)
    weekend_days = get_weekend_days_between(start, now)
    personal_holidays = get_personal_holidays_between(config, start, now)
    company_holidays = get_company_holidays_between(config, start, now)
    full_timespan = now - start
    if log.verbose:
        click.echo('Calculating current work hour balance...')
    days_to_work = full_timespan.days - bank_holidays \
        - weekend_days - personal_holidays - company_holidays
    hours_to_work = (days_to_work + 1) * config['working_day_hours']
    to_work = datetime.timedelta(seconds=(hours_to_work * 3600))
    print_balance(to_work, worked)


# Required for debugging:
if __name__ == "__main__":
    main()
