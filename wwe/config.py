import json
import os


def load_config(path='.wwe/config.json'):
    """Load and return configuration file.

    If no path is provided, default configuration (~/.wwe/config.json)
    is loaded.
    """
    user_home_path = os.path.expanduser('~')
    config_path = os.path.join(user_home_path, path)
    return import_json_file(config_path)


def import_json_file(path: str):
    """Import JSON configuration file."""
    with open(path) as fd:
        config = json.load(fd)
    return config
