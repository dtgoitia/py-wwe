import json
import os
import platform
import wwe.log as log


def get_default_config_path():
    """Return default configuration file path depending on the OS."""
    user_home_path = os.path.expanduser('~')
    system = platform.system()
    if system == 'Linux':
        path = r'.config/wwe/config.json'
    if system == 'Windows':
        path = r'.config\wwe\config.json'
    config_path = os.path.join(user_home_path, path)
    return config_path


def load_config(path=None) -> dict:
    """Load and return configuration file.

    If no path is provided, default configuration is loaded from
    the config folder: ~/.config/wwe/config.json
    """
    if path is None:
        config_path = get_default_config_path()
    if log.verbose:
        print(f'Loading configuration from "{config_path}"...')
    return import_json_file(config_path)


def import_json_file(path: str):
    """Import JSON configuration file."""
    with open(path) as fd:
        config = json.load(fd)
    return config
