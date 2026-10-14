from data.post_data import post_data

def test_get_post(post_api):

    response = post_api.get_post(1)


    data = response.json()


    assert response.status_code == 200


    assert data["id"] == 1


    assert "title" in data

def test_create_post(post_api):

    response = post_api.create_post(
        post_data
    )    

    result = response.json()

    assert response.status_code == 201

    assert result["title"] == "python-test"

    assert result["userId"] == 1