import json


def import_config(path: str):
    """Import JSON configuration file."""
    with open(path) as fd:
        config = json.load(fd)
    return config
