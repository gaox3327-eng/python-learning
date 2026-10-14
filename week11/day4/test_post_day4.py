from api_client import ApiClient


api = ApiClient()


def test_create_post():

    url = "https://jsonplaceholder.typicode.com/posts"


    data = {
        "title":"python-test",
        "body":"day4",
        "userId":1
    }


    response = api.post(
        url,
        data
    )


    result = response.json()


    assert response.status_code == 201

    assert result["title"] == "python-test"