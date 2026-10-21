import pytest
@pytest.mark.parametrize("post_id",[1,2,3])
def test_get_post(post_api,post_id):

    response = post_api.get_post(post_id)


    data = response.json()


    assert response.status_code == 200

    assert data["id"] == post_id

    assert "body" in data
    assert "userId" in data
    assert "title" in data

