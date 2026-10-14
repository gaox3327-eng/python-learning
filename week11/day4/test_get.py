from api_client import ApiClient


api = ApiClient()


def test_get_post():

    url = "https://jsonplaceholder.typicode.com/posts/1"


    response = api.get(url)


    result = response.json()


    assert response.status_code == 200

    assert result["id"] == 1

    assert "title" in result