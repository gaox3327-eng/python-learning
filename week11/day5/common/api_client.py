import requests


class ApiClient:

    def get(self, url, params=None, headers=None):

        response = requests.get(
            url,
            params=params,
            headers=headers
        )

        return response


    def post(self, url, data=None, headers=None):

        response = requests.post(
            url,
            json=data,
            headers=headers
        )

        return response