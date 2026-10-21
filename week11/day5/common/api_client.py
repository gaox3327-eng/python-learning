import requests
from config.config import BASE_URL

class ApiClient:

    def get(self, url, params=None, headers=None):

        response = requests.get(
            BASE_URL+url,
            params=params,
            headers=headers
        )

        return response


    def post(self, url, data=None, headers=None):

        response = requests.post(
            BASE_URL+url,
            json=data,
            headers=headers
        )

        return response