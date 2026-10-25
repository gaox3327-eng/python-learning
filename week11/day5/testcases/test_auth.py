"""第 5 课：鉴权用例（目标接口 httpbin.org）

三类场景：
    1. 没有凭据 / 格式错 / 空 token  → 401
    2. 正确 token                    → 200，且回显的就是我传的
    3. Basic Auth 正确 / 错误凭据     → 200 / 401
"""

import pytest

from common.api_client import ApiClient
from config.config import AUTH_TOKEN, AUTH_BASE_URL


@pytest.fixture
def anon_client():
    """不带任何凭据的客户端。"""
    return ApiClient(base_url=AUTH_BASE_URL)


@pytest.fixture
def bearer_client():
    """带正确 Bearer token 的客户端。"""
    return ApiClient(
        base_url=AUTH_BASE_URL,
        headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
    )


# ---------------------------------------------------------------- Bearer
def test_bearer_without_token_returns_401(anon_client):
    """不带 token → 401"""
    resp = anon_client.get("/bearer")
    assert resp.status_code == 401


def test_bearer_with_valid_token_returns_200_and_echoes_token(bearer_client):
    """正确 token → 200，且响应里的 token 就是我传的那个（业务断言）"""
    resp = bearer_client.get("/bearer")
    assert resp.status_code == 200
    assert resp.json()["token"] == AUTH_TOKEN


def test_bearer_with_malformed_token_returns_401(anon_client):
    """少了 'Bearer ' 前缀 → 401（格式错也是错）"""
    client = ApiClient(
        base_url=AUTH_BASE_URL,
        headers={"Authorization": AUTH_TOKEN},     # 故意不加 Bearer 前缀
    )
    resp = client.get("/bearer")
    assert resp.status_code == 401


def test_bearer_with_empty_token_returns_401(anon_client):
    """Bearer 后面是空的 → 401"""
    client = ApiClient(
        base_url=AUTH_BASE_URL,
        headers={"Authorization": "Bearer "},
    )
    resp = client.get("/bearer")
    assert resp.status_code == 401


# ---------------------------------------------------------------- Basic Auth
def test_basic_auth_with_valid_credentials_returns_200(anon_client):
    """Basic Auth 正确凭据 → 200

    注意：业务层没有封装 basic auth，所以用底层 request() 临时调用。
    这比为了一个用例去改 get() 的签名更干净。
    """
    resp = anon_client.request("GET", "/basic-auth/alice/secret",
                               auth=("alice", "secret"))
    assert resp.status_code == 200
    assert resp.json()["user"] == "alice"


def test_basic_auth_with_wrong_credentials_returns_401(anon_client):
    """Basic Auth 错误凭据 → 401"""
    resp = anon_client.request("GET", "/basic-auth/alice/secret",
                               auth=("alice", "wrong-password"))
    assert resp.status_code == 401