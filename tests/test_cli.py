from typing import Tuple

import pytest
from click.testing import CliRunner
from wwe.cli import main


# TODO: mock Toggle API to return a known set of time entries
# TODO: do a single end to end test


@pytest.mark.integration
def test_main():
    """Run the main command without arguments or flags."""
    runner = CliRunner()
    result = runner.invoke(main, [])

    if result.exit_code == 1:
        raise result.exception

    assert result.exit_code == 0
    # TODO: assert output format


@pytest.mark.integration
@pytest.mark.parametrize('arguments', (
    ('--end 2018-02-06'),
    ('-e 2018-02-06'),
))
def test_end_date(arguments: Tuple[str]):
    """Calculate the balance until a given end date."""
    runner = CliRunner()
    result = runner.invoke(main, arguments)

    if result.exit_code == 1:
        raise result.exception

    assert result.exit_code == 0
    # TODO: assert output format
