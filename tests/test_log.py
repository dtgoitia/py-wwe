import pytest

from wwe.log import format_log, set_verbose_mode


@pytest.fixture
def verbose_on():
    set_verbose_mode(True)


def test_format_log(mock_entry, verbose_on):
    expected_result = "2018-02-05 10:00:13-12:00:32 General"
    result = format_log(mock_entry)
    assert expected_result == result
