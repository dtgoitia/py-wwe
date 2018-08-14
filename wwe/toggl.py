from datetime import datetime, timedelta, date
from wwe.toggl_api import TogglAPI
from tzlocal import get_localzone
# import pprint


def filter_entries(entries, filters):
    """Apply filters to entries.

    Every entry in `entries` with satisfies all the filters will be yielded. A filter is a function which returns
    `True` or `False` given an `entry`.
    """
    for entry in entries:
        for filter_func in filters:
            if not filter_func(entry):
                break
        else:
            yield entry


def ensure_datetime_timezone(timestamp):
    """Ensure timezone is set."""
    if timestamp is None:
        return
    current_tz = timestamp.tzinfo
    local_tz = get_localzone()
    if current_tz == local_tz:
        return timestamp
    return timestamp.astimezone(local_tz)


class TogglWrap:
    """Toggl Client wrapper."""

    def __init__(self, token=""):
        """Instantiate TogglAPI client if there a token is passed."""
        assert token
        self.toggl = TogglAPI(api_token=token)

    def get_filtered_entries(self, filters, start: datetime=None, end: datetime=None):
        """Return only the entries between two given dates which pass the passed `filters`."""
        if start is None:
            start = datetime.combine(date.today(), datetime.min.utctime())
        start, end = (ensure_datetime_timezone(x) for x in (start, end))
        entries = self.toggl.get_time_entries(start_date=start, end_date=end)
        for entry in filter_entries(entries, filters):
            yield entry

    def _client_by_id(self, client_id: int):
        if not hasattr(self, "_clients"):
            self.clients()
        if not hasattr(self, "_clients"):
            raise Exception('cannot fetch clients from Toggl')

        for c in self._clients:
            if c["id"] == client_id:
                return c

        raise Exception(f"client {client_id} not found!")

    def _project_by_client(self, client_name: str):
        if not hasattr(self, "_clients"):
            self.clients()
        if not hasattr(self, "_clients"):
            raise Exception('cannot fetch clients from Toggl')
        if not hasattr(self, "_projects"):
            self.projects()
        if not hasattr(self, "_projects"):
            raise Exception('cannot fetch projects from Toggl')

        result = []
        for p in self._projects:
            if "cid" in p:
                for c in self._clients:
                    if c["name"] == client_name and p["cid"] == c["id"]:
                        new_p = p
                        new_p["client"] = c["name"]
                        result.append(new_p)
        return result

    def clients(self):
        """Return all clients in all workspaces."""
        w = self.toggl.workspaces()
        id = w[0]["id"]
        clients = self.toggl.clients(workspace_id=id)

        result = []
        for p in clients:
            result.append({
                "id": p["id"],
                "name": p["name"],
            })

        if len(result) > 0:
            self._clients = result

        print("---fetching clients!")
        return result

    def projects(self):
        """Return all projects in all workspaces."""
        w = self.toggl.workspaces()
        id = w[0]["id"]
        projects = self.toggl.projects(workspace_id=id)

        result = []
        for p in projects:
            result.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "cid": p.get("cid", "none"),
            })

        if len(result) > 0:
            self._projects = result

        print("---fetching projects!")
        return result

    def tasks(self, start: datetime, end: datetime, client=""):
        """Return tasks from Toggl between two given dates for a client."""
        if self.toggl is not None:
            if start is not None and end is not None:
                projects = self._project_by_client(client)

                print("\nfetching your tasks!")
                s = start.isoformat()
                e = (end + timedelta(days=1)).isoformat()
                entries = self.toggl.get_time_entries(
                    start_date=s, end_date=e)

                for entry in entries:
                    for p in projects:
                        if entry["pid"] == p["id"]:
                            entry["project"] = p["name"]
                            entry["client"] = p["client"]
                return entries
