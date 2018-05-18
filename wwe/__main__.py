# # POC: import config
# from wwe.config import importConfig
# config = importConfig('./config.json')
# token = config['toggl']['token']
# print(token)

# # POC: Toggl API wrapper
# from tapioca_toggl import Toggl
# api = Toggl(access_token=token)
# me = api.me_with_related_data().get()
# print(me)

# # POC: UK bank holidays
# import requests
# bank_holiday_url = "https://www.gov.uk/bank-holidays.json"
# r = requests.get(bank_holiday_url)
# print(r.json())
from .recorder import Task, Holiday, BankHoliday, PersonalHoliday, Recorder
from datetime import datetime

task1 = Task(
    project="Bot Builder",
    task="General",
    start=datetime(2018, 5, 10, 9, 0, 0),
    end=datetime(2018, 5, 10, 9, 0, 25)
)

task2 = Task(
    project="Bot Builder",
    task="General",
    start=datetime(2018, 5, 12, 9, 0, 0),
    end=datetime(2018, 5, 12, 9, 0, 25)
)

holiday = Holiday(datetime(2018, 5, 11))
bank_holiday = BankHoliday(datetime(2018, 5, 13))
personal_holiday = PersonalHoliday(datetime(2018, 5, 14))

start = datetime(2018, 3, 28)
end = datetime(2018, 4, 4)
bh = BankHoliday(date=datetime(2018, 4, 2))  # Easter Monday
r = Recorder()
# r.add(bh)
actual_result = r.total_hours_to_work(start, end)
print(f"actual_result = {actual_result}")
