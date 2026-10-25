import pytest

from api.post_api import PostApi
from common.api_client import ApiClient
from common.auth import bearer
from config.config import AUTH_TOKEN, AUTH_BASE_URL


# ---------------------------------------------------------------- 原有夹具
@pytest.fixture
def post_api():
    """被测业务接口（jsonplaceholder，无需鉴权）。

    注意：必须保留 —— test_post_day5.py 的 8 个用例全靠它。
    """
    return PostApi()


# ---------------------------------------------------------------- 鉴权夹具
def _refresh_credentials(client):
    """凭据刷新。

    真实项目里这里是：调登录接口 → 拿新 token → 写回 client.default_headers
    现在用 httpbin 演示，token 从 .env 读。
    """
    client.default_headers.update(bearer(AUTH_TOKEN))


@pytest.fixture
def auth_api():
    """带鉴权 + 自动续期的客户端（httpbin）。

    目前用例未直接使用：PostApi 的方法（/posts/...）在 httpbin 上不存在。
    保留它用于演示「依赖注入 + 401 自动续期」，
    后续要为它单独写一组指向 httpbin 的业务方法，或在选做测试里用。
    """
    client = ApiClient(base_url=AUTH_BASE_URL, on_unauthorized=_refresh_credentials)
    return PostApi(client=client)