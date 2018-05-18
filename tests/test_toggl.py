# from wwe.toggl import TogglWrap


def test_empty(mock_config):
    c = mock_config
    assert c.get("toggl").get("timezone") == "+00:00"
