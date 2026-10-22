from common.api_client import ApiClient

class PostApi:

    def __init__(self):

        self.client = ApiClient()

    def get_post(self,post_id):

        url = f"/posts/{post_id}"

        response = self.client.get(url)

        return response

    def create_post(self,data):

        urI = "/posts"

        response = self.client.post(
            urI,
            data = data
        )

        return response
    def delete_post(self,post_id):
    
            url = f"/posts/{post_id}"
    
            response = self.client.delete(url)
    
            return response