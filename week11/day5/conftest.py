import pytest

from api.post_api import PostApi
from api.products_api import ProductsApi
from common.api_client import ApiClient
from common.auth import bearer
from config.config import AUTH_TOKEN, AUTH_BASE_URL

DUMMY_BASE = "https://dummyjson.com"


# ---------------------------------------------------------------- 业务夹具
@pytest.fixture
def post_api():
    """jsonplaceholder 业务接口（无需鉴权）。test_post_day5.py 的 8 个用例依赖它。"""
    return PostApi()


@pytest.fixture
def dummy_client():
    """指向 dummyjson 的底层客户端（无鉴权）。"""
    return ApiClient(base_url=DUMMY_BASE)


@pytest.fixture
def products_api(dummy_client):
    """dummyjson/products 的业务接口（注入底层客户端）。"""
    return ProductsApi(client=dummy_client)


# ---------------------------------------------------------------- 鉴权演示夹具
def _refresh_credentials(client):
    """凭据刷新：真实项目里是调登录接口拿新 token 后写回默认头。"""
    client.default_headers.update(bearer(AUTH_TOKEN))


@pytest.fixture
def auth_api():
    """带鉴权 + 401 自动续期的客户端（httpbin）。

    注意：test_auth.py 自己定义了 anon_client / bearer_client 两个本地夹具，
    不依赖这里；本夹具仅用于演示依赖注入与续期机制。
    """
    client = ApiClient(base_url=AUTH_BASE_URL, on_unauthorized=_refresh_credentials)
    return PostApi(client=client)
