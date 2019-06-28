import datetime
from typing import Any, Dict


def set_verbose_mode(verbose_mode: bool) -> None:
    """Set verbose mode value globally so that children functions can access it."""
    global verbose
    verbose = verbose_mode


def format_log(time_entry: Dict[str, Any]) -> None:
    """Log a given time entry."""
    if not verbose:
        return
    day = datetime.datetime.strftime(time_entry['start'], '%Y-%m-%d')
    start = datetime.datetime.strftime(time_entry['start'], '%H:%M:%S')
    stop = datetime.datetime.strftime(time_entry['stop'], '%H:%M:%S')
    return f"{day} {start}-{stop} {time_entry['description']}"
