from data.post_data import post_data

def test_get_post(post_api):

    response = post_api.get_post(1)


    data = response.json()


    assert response.status_code == 200


    assert data["id"] == 1

    assert "body" in data
    assert "userId" in data
    assert "title" in data

def test_create_post(post_api):

    response = post_api.create_post(
        post_data
    )    

    result = response.json()

    assert response.status_code == 201
    assert result["title"] == post_data["title"]
    assert result["body"] == post_data["body"]
    assert result["userId"] == post_data["userId"]
    assert "id" in result

def test_get_another_post(post_api):
    response = post_api.get_post(2)

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 2
    assert "title" in data
    assert "body" in data

def test_get_post_3(post_api):
    response = post_api.get_post(3)

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == 3
    assert "title" in data
    assert "body" in data    