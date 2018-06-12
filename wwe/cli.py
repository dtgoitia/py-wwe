from pprint import pprint as print
import functools
from wwe.toggl import TogglWrap
from wwe.config import import_config
from wwe.recorder import Task, BankHoliday, PersonalHoliday, Recorder
from wwe.gov import gov_uk_bank_holidays_between
from typing import List
import datetime


def toggl_entry_to_task(entry: dict) -> Task:
    start = entry.get('start')
    end = entry.get('stop', datetime.now())
    project = entry.get('project')
    description = entry.get('description')
    task = Task(start, end, project, description)
    return task


def toggl_entries_to_tasks(entries: set) -> set:
    result = set()
    for entry in entries:
        task = toggl_entry_to_task(entry)
        result.add(task)
    return result


def fetch_tasks(toggl_token: str, start: datetime) -> set:
    t = TogglWrap(token=toggl_token)
    toggl_tasks = t.tasks_from(start)
    tasks = toggl_entries_to_tasks(toggl_tasks)
    return tasks


def gov_to_bank_holidays(gov_bank_holidays: set) -> set:
    bank_holidays = set()
    for gov_bank_holiday in gov_bank_holidays:
        bank_holiday = BankHoliday(gov_bank_holiday)
        bank_holidays.add(bank_holiday)
    return bank_holidays


def fetch_bank_holidays(start: datetime) -> set:
    end = datetime.datetime.now()
    gov_bank_holidays = gov_uk_bank_holidays_between(start, end)
    bank_holidays = gov_to_bank_holidays(gov_bank_holidays)
    return bank_holidays


def fetch_personal_holidays(config_personal_holidays: list, start: datetime.datetime) -> set:
    result = set()
    for day in config_personal_holidays:
        date = datetime.datetime.strptime(day, '%Y-%m-%d')
        personal_holiday = PersonalHoliday(date)
        result.add(personal_holiday)
    return result


def main2():
    config = import_config('./config.json')
    start_date = config['client']['start_date']
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')

    tasks = fetch_tasks(config['toggl_token'], start)
    bank_holidays = fetch_bank_holidays(start)
    personal_holidays = fetch_personal_holidays(config['client']['personal_holidays']['scheduled'], start)

    r = Recorder(config['working_day_hours'])
    r.add(tasks)
    r.add(bank_holidays)
    r.add(personal_holidays)

    summary = r.summary()
    print(summary)


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


def main():
    config = import_config('./config.json')
    toggl_token = config['toggl_token']
    start = datetime.datetime.strptime(config['client']['start_date'], '%Y-%m-%d')
    t = TogglWrap(token=toggl_token)
    project_ids = get_project_ids(target_client=config['client']['name'], t=t)
    filters = [functools.partial(is_work, work_projects=project_ids)]
    total_duration = datetime.timedelta()
    for entry in t.get_filtered_entries(filters=filters, start=start):
        duration = entry['duration']
        total_duration += duration
    print(str(total_duration))
