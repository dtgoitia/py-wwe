import pytest


@pytest.fixture
def mock_config():
    return {
        "toggl": {
            "token": "870738agd54db0e63qfd943380ahbe8f",
            "timezone": "+00:00"
        }
    }
