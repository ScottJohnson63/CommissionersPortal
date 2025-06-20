import glob
import json
import os
import requests
from types import SimpleNamespace

CONFIG_FILE = 'config.json'

# def load_config(file_path):
#     with open(file_path, 'r') as f:
#         return json.load(f)

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
    config = load_configs()
    leagues = config.leagues
    if not leagues:
        print('No leagues found in config file.')
        return
    for league_name, url in leagues.items():
        result = make_request(url)
        print(f'League: {league_name}')
        print(json.dumps(result, indent=2))
        print('-' * 40)

def get_config_dir():
    """
    Returns the directory where configuration files are stored.
    Adjust the path as needed; here, config files are assumed to be in 'conf/'.
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'conf'))

# Use a relative path for the config directory and handle missing config files
def load_configs():
    config_dir = get_config_dir()
    files = glob.glob(os.path.join(config_dir, '*.json'))
    config = {}
    if not files:
        raise FileNotFoundError(f"No config files found in {config_dir}")
    for file in files:
        with open(file, 'r') as f:
            config.update(json.load(f))
    return json.loads(json.dumps(config), object_hook=lambda d:SimpleNamespace(**d)) # Convert to SimpleNamespace for easier attribute access

if __name__ == '__main__':
    main()