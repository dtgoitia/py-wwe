# Credit to Mosab Ibrahim <mosab.a.ibrahim@gmail.com>

import requests
import click
import datetime
import wwe.log as log

from requests.auth import HTTPBasicAuth

TOGGL_TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S'


def write_toggl_timestamp(ts: datetime.datetime):
    """Write datetime in toggl format or default to empty string."""
    if not ts:
        return ''
    tz = ts.strftime('%z')
    if tz:
        tz = f'{tz[:3]}:{tz[3:]}'
    else:
        tz = '+00:00'
    return ts.strftime(TOGGL_TIMESTAMP_FORMAT) + tz


def read_toggl_timestamp(text: str):
    """Read datetime in toggl format or return None."""
    try:
        ts, _, tz_2 = text.rpartition(':')
        ts = datetime.datetime.strptime(ts + tz_2, '%Y-%m-%dT%H:%M:%S%z')
        return ts
    except (ValueError, AttributeError) as e:
        return text


def deserialize_toggl(obj):
    """Deserialize Toggl object."""
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
    else:
        new_obj = obj
    return new_obj


class TogglAPI(object):
    """A wrapper for Toggl API."""

    def __init__(self, api_token):
        """Initialize client."""
        if log.verbose:
            click.echo('Instantiating Toggle API...')
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(api_token, 'api_token')
        self.session.headers = {'content-type': 'application/json'}

    def get(self, section, params=None):
        """Request resources Toggl API endpoint."""
        response = self.session.get(
            f'https://www.toggl.com/api/v8/{section}', params=params)
        if not response.ok:
            raise ValueError(response.text)
        return response.json()

    def get_time_entries(self, start_date: datetime.datetime, end_date: datetime.datetime = None):
        """Get Time Entries JSON object from Toggl within a given start_date and an end_date with a given timezone.

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
        assert start_date.tzinfo is not None
        if end_date:
            assert end_date.tzinfo is not None
        request_parameters = {
            'start_date': write_toggl_timestamp(start_date),
            'end_date': write_toggl_timestamp(end_date),
        }

        last_entry_date = datetime.datetime(datetime.MINYEAR, 1, 1, tzinfo=start_date.tzinfo)
        if end_date is None:
            end_date = datetime.datetime(datetime.MAXYEAR, 1, 1, tzinfo=start_date.tzinfo)
        if log.verbose:
            click.echo(f'Fetching time entries from {start_date} to {end_date}...')
        while last_entry_date < end_date:
            response = self.get(section='time_entries', params=request_parameters)
            entries = deserialize_toggl(response)
            if not entries:
                break
            for entry in entries:
                yield entry
                last_entry_date = entry['start']
            if log.verbose:
                click.echo(f"  >> {request_parameters['start_date']} - {last_entry_date}")
            request_parameters['start_date'] = write_toggl_timestamp(last_entry_date + datetime.timedelta(seconds=1))

    def get_clients(self, workspace_id):
        """Get Projects by Workspace ID."""
        if log.verbose:
            click.echo(f'Toggl API: fetching clients under {workspace_id} workspace...')
        return self.get(section=f'workspaces/{workspace_id}/clients')

    def get_projects(self, workspace_id):
        """Get Projects by Workspace ID.

        [{'active': True,
          'actual_hours': 9,
          'at': '2018-03-02T13:59:37+00:00',
          'auto_estimates': False,
          'billable': False,
          'cid': 38084455,
          'color': '11',
          'created_at': '2018-02-06T08:10:31+00:00',
          'hex_color': '#205500',
          'id': 97990398,
          'is_private': False,
          'name': 'Software Imaging',
          'template': False,
          'wid': 1819588}]
        """
        if log.verbose:
            click.echo(f'Toggl API: fetching projects under {workspace_id} workspace...')
        return self.get(section=f'workspaces/{workspace_id}/projects')

    def get_workspaces(self):
        """Get Workspaces.

        [{'admin': True,
           'api_token': '3e609bd47750eb70df49d1e8182e6bd5',
           'at': '2016-12-28T02:26:24+00:00',
           'default_currency': 'USD',
           'default_hourly_rate': 0,
           'ical_enabled': True,
           'id': 1819588,
           'name': "David Torralba Goitia's workspace",
           'only_admins_may_create_projects': False,
           'only_admins_see_billable_rates': False,
           'only_admins_see_team_dashboard': False,
           'premium': False,
           'profile': 0,
           'projects_billable_by_default': True,
           'rounding': 1,
           'rounding_minutes': 0}]
        """
        if log.verbose:
            click.echo('Toggl API: fetching workspaces...')
        return self.get(section='workspaces')

    def get_me(self):
        """Request resources Toggl API endpoint with the 'me' section."""
        return self.get(section='me')
