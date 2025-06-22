import glob
import json
import os
import requests
from types import SimpleNamespace
import sys

CONFIG_FILE = 'config.json'

def make_request(url):
    """
    Makes a GET request to the given URL and returns the response as JSON if possible.
    Returns a dict with status_code, json (if available), and error (if any).
    """
    try:
        response = requests.get(url)
        try:
            data = response.json()
        except ValueError:
            data = None
        return {
            'url': url,
            'status_code': response.status_code,
            'json': data,
            'error': None
        }
    except Exception as e:
        return {
            'url': url,
            'status_code': None,
            'json': None,
            'error': str(e)
        }

def main():
    config = load_config()
    leagues = config.leagues
    if not leagues:
        print('No leagues found in config file.')
        return
    for league_name, url in leagues.items():
        result = make_request(url)
        print(f'League: {league_name}')
        print(json.dumps(result, indent=2))
        print('-' * 40)

def resource_path(relative_path):
    """
    Get the absolute path to a resource, works for both development and frozen (PyInstaller) modes.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_config_dir():
    """
    Returns the directory where configuration files are stored.
    Adjust the path as needed; here, config files are assumed to be in 'conf/'.
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'conf'))

# Use a relative path for the config directory and handle missing config files
def load_config():
    config_dir = resource_path('conf')
    files = glob.glob(os.path.join(config_dir, CONFIG_FILE))
    config = {}
    if not files:
        raise FileNotFoundError(f"No config files found in {config_dir}")
    for file in files:
        with open(file, 'r') as f:
            config.update(json.load(f))
    return json.loads(json.dumps(config), object_hook=lambda d:SimpleNamespace(**d)) # Convert to SimpleNamespace for easier attribute access

def load_descriptions():
    """
    Loads setting and scoring descriptions from the config file.
    Returns a dictionary with descriptions.
    """
    config_dir = get_config_dir()
    description_files = glob.glob(os.path.join(config_dir, '*_descriptions.json'))
    if not description_files:
        raise FileNotFoundError(f"No description files found in {config_dir}")
    descriptions = {}
    for file in description_files:
        with open(file, 'r') as f:
            descriptions.update(json.load(f))
    return descriptions

if __name__ == '__main__':
    main()