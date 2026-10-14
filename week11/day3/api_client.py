import requests

class ApiClient:

    def get(self,urI,params=None,headers=None):

        response = requests.get(
                    urI,
                    params=params,
                    headers=headers
            )
        return response 

    def post(self,urI,data=None,headers=None):

        response = requests.post(
            urI,
            json=data,
            headers=headers
        )

        return response