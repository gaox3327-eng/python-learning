from common.api_client import ApiClient

class PostApi:

    def __init__(self, client=None):
        # 不传就自己造；传了就用传入的（依赖注入，方便测试与复用）
        self.client = client or ApiClient()

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