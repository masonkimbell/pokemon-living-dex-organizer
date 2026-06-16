import requests

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}

    def get(self, endpoint: str, params: dict = {}) -> tuple[dict, int]:
        url = self.base_url + '/' + endpoint
        response = requests.get(url, params)
        return response.json(), response.status_code
