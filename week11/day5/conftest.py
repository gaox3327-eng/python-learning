import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

from api.post_api import PostApi
from api.products_api import ProductsApi
from common.api_client import ApiClient
from common.auth import bearer
from config.config import AUTH_TOKEN, AUTH_BASE_URL

ROOT = Path(__file__).resolve().parent
DUMMY_BASE = "https://dummyjson.com"
MOCK_URL = "http://127.0.0.1:8001"


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


# ---------------------------------------------------------------- 第 8 课：本地 mock 服务
def _mock_alive() -> bool:
    try:
        requests.get(MOCK_URL + "/products", params={"limit": 1}, timeout=1)
        return True
    except requests.RequestException:
        return False


@pytest.fixture(scope="session")
def mock_server():
    """整个会话启动一次本地商城服务；测试结束自动关掉。

    yield 之前 = setup，yield 之后 = teardown。
    如果 8001 上已经有服务在跑（手工启动的），直接复用，不重复启动也不负责关闭。
    """
    if _mock_alive():
        yield MOCK_URL
        return

    proc = subprocess.Popen(
        [sys.executable, str(ROOT / "server.py"), "8001"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    for _ in range(50):                      # 最多等 5 秒
        if _mock_alive():
            break
        time.sleep(0.1)
    else:
        proc.kill()
        raise RuntimeError("mock server 启动失败：检查 server.py 与 8001 端口")

    yield MOCK_URL

    proc.kill()
    proc.wait(timeout=5)


@pytest.fixture
def shop(mock_server):
    """每条用例前重置数据，保证互相隔离；短超时（本地服务，慢就是真有问题）。"""
    requests.post(mock_server + "/reset", timeout=5)
    return ApiClient(base_url=mock_server, timeout=5, retries=0)
