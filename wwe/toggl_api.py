# Credit to Mosab Ibrahim <mosab.a.ibrahim@gmail.com>

import requests
import datetime

from requests.auth import HTTPBasicAuth

TOGGL_TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S'


def write_toggl_timestamp(ts: datetime.datetime):
    """
    Write datetime in toggl format or default to empty string
    """
    if not ts:
        return ''
    tz = ts.strftime('%z')
    if tz:
        tz = f'{tz[:2]}:{tz[3:]}'
    else:
        tz = '+00:00'
    return ts.strftime(TOGGL_TIMESTAMP_FORMAT) + tz


def read_toggl_timestamp(text: str):
    """
    Read datetime in toggl format or return None
    """
    try:
        ts, _, tz_2 = text.rpartition(':')
        ts = datetime.datetime.strptime(ts+tz_2, '%Y-%m-%dT%H:%M:%S%z')
        return ts
    except (ValueError, AttributeError) as e:
        return None


def deserialize_toggl(obj):
    new_obj = None
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if k in ['duration'] and isinstance(v, int):
                new_obj[k] = datetime.timedelta(seconds=v)
                continue
            new_obj[k] = deserialize_toggl(v)
    elif isinstance(obj, list):
        new_obj = []
        for v in obj:
            new_obj.append(deserialize_toggl(v))
    elif isinstance(obj, str):
        new_obj = read_toggl_timestamp(obj)
        if new_obj is None:
            new_obj = obj
    else:
        new_obj = obj
    return new_obj


class TogglAPI(object):
    """A wrapper for Toggl Api"""

    def __init__(self, api_token):
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(api_token, 'api_token')
        self.session.headers = {'content-type': 'application/json'}

    def get(self, section, params=None):
        response = self.session.get(
            f'https://www.toggl.com/api/v8/{section}', params=params)
        if not response.ok:
            raise ValueError(response.text)
        return response.json()

    def clients(self, workspace_id):
        """Get Projects by Workspace ID"""
        section = f'workspaces/{workspace_id}/clients'
        return self.get(section=section)

    def get_time_entries(self, start_date: datetime.datetime=None, end_date: datetime.datetime =None):
        """
        Get Time Entries JSON object from Toggl within a given start_date
        and an end_date with a given timezone
         {'at': '2018-05-23T15:04:45+00:00',
          'billable': False,
          'description': 'General',
          'duration': 615,
          'duronly': False,
          'guid': 'e6a5763ae8e13e4dac9afd460e7a085d',
          'id': 880947808,
          'pid': 97990658,
          'start': '2018-05-23T14:54:29+00:00',
          'stop': '2018-05-23T15:04:44+00:00',
          'tags': ['software imaging'],
          'uid': 2626092,
          'wid': 1819588},
        """
        p = {
            'start_date': write_toggl_timestamp(start_date),
            'end_date': write_toggl_timestamp(end_date),
        }
        response = self.get(section='time_entries', params=p)
        return deserialize_toggl(response)

    def projects(self, workspace_id=''):
        """Get Projects by Workspace ID"""
        section = f'workspaces/{workspace_id}/projects'
        return self.get(section=section)

    def workspaces(self):
        """Get Workspaces"""
        section = f'workspaces'
        return self.get(section=section)

    def me(self):
        return self.get(sec)
