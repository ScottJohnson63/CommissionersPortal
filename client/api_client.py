import requests

API_BASE_URL = 'http://127.0.0.1:5000/api'

def get_config():
    resp = requests.get(f'{API_BASE_URL}/config')
    resp.raise_for_status()
    return resp.json()

def make_request(url):
    resp = requests.get(url)
    try:
        data = resp.json()
    except Exception:
        data = None
    return {
        'data': data,
        'status_code': resp.status_code,
        'url': url
    }
