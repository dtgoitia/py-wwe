from pprint import pprint as print
import functools
from wwe.toggl import TogglWrap
from wwe.config import import_config
from wwe.gov import gov_uk_bank_holidays_between
from typing import List
import datetime
import os


# (start, end)
# (00:00:00, 23:59:59)
# (08:30:00, 16:00:00)

def partition_days_between(start_date: datetime.datetime, end_date: datetime.datetime):
    """
    Generates a stream of tuples with two datetimes that run from the
    start_date to the end_date.

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
    for start, end in times:
        if start.weekday() < 5:
            yield (start, end)


def filter_out_non_working_hours(times):
    for start, end in times:
        pass


def get_project_ids(target_client: str, t: TogglWrap):
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
    # print(f'{entry["pid"]} in {work_projects}')
    if entry['pid'] in work_projects:
        return True
    return False


def get_weekends_between(start: datetime.datetime, end: datetime.datetime) -> int:
    result = 0
    current_date = start
    while current_date < end:
        if current_date.weekday() > 4:
            result += 1
        current_date += datetime.timedelta(days=1)
    return result


def get_personal_holidays(days: any, start: datetime.datetime, end: datetime.datetime) -> float:
    result = 0
    for day in days:
        current_day = datetime.datetime.strptime(day[0], '%Y-%m-%d')
        if start <= current_day <= end:
            result += float(day[1])
    return result


def format_balance(delta: datetime.timedelta) -> str:
    """
    Remove the microseconds from the time delta
    """
    return str(datetime.timedelta(days=delta.days) + datetime.timedelta(seconds=delta.seconds))


def print_balance(to_work: datetime.datetime, worked: datetime.datetime):
    if to_work > worked:
        print(f"balance = {format_balance(to_work-worked)} left")
    else:
        print(f"balance = {format_balance(worked-to_work)} done extra")


def main():
    config_path = os.path.join(os.environ["HOMEPATH"], ".wweconfig.json")
    config = import_config(config_path)
    toggl_token = config['toggl_token']
    start = datetime.datetime.strptime(config['client']['start_date'], '%Y-%m-%d')
    t = TogglWrap(token=toggl_token)
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
    bank_holidays = len(gov_uk_bank_holidays_between(start, now))
    weekends = get_weekends_between(start, now)
    personal_holidays = get_personal_holidays(config['personal_holidays'], start, now)
    full_timespan = now - start
    days_to_work = full_timespan.days - bank_holidays - weekends - personal_holidays
    hours_to_work = (days_to_work + 1) * config['working_day_hours']
    to_work = datetime.timedelta(seconds=(hours_to_work*3600))
    print_balance(to_work, worked)


# # Uncomment below to debug
# if __name__ == "__main__":
#     main()
