import datetime

import pytest


@pytest.fixture
def mock_config():
    return {
        "toggl": {
            "token": "870738agd54db0e63qfd943380ahbe8f",
            "timezone": "+00:00"
        }
    }


@pytest.fixture
def mock_entry():
    return {"at": datetime.datetime(2019, 3, 4, 8, 7, 58, tzinfo=datetime.timezone.utc),
            "billable": False,
            "description": "General",
            "duration": 615,
            "duronly": False,
            "guid": "e6a5763ae8e13e4dac9afd460e7a085d",
            "id": 880947808,
            "pid": 97990658,
            "start": datetime.datetime(2018, 2, 5, 10, 0, 13, tzinfo=datetime.timezone.utc),
            "stop": datetime.datetime(2018, 2, 5, 12, 0, 32, tzinfo=datetime.timezone.utc),
            "tags": ["software imaging"],
            "uid": 2626092,
            "wid": 1819588}
