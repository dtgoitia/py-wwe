import json
import os
import wwe.log as log


def load_config(path='.config/wwe/config.json'):
    """Load and return configuration file.

    If no path is provided, default configuration is loaded from
    the config folder: ~/.config/wwe/config.json
    """
    user_home_path = os.path.expanduser('~')
    config_path = os.path.join(user_home_path, path)
    if log.verbose:
        print(f'Pulling configuration from "{config_path}"...')
    return import_json_file(config_path)


def import_json_file(path: str):
    """Import JSON configuration file."""
    with open(path) as fd:
        config = json.load(fd)
    return config
