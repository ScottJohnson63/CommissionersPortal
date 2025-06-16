import json
import requests

CONFIG_FILE = 'config.json'

def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

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
    config = load_config(CONFIG_FILE)
    leagues = config.get('leagues', {})
    if not leagues:
        print('No leagues found in config file.')
        return
    for league_name, url in leagues.items():
        result = make_request(url)
        print(f'League: {league_name}')
        print(json.dumps(result, indent=2))
        print('-' * 40)

if __name__ == '__main__':
    main()