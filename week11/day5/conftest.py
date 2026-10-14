import pytest

from api.post_api import PostApi


@pytest.fixture
def post_api():

    api = PostApi()

    return api