"""第 7 课 Day 2：幂等性验证

前置条件：先启动有状态服务
    python D:\\大肥鱼\\学习\\07-异常与容错\\idem_server.py 8002
"""

import pytest
import requests

from common.api_client import ApiClient

BASE = "http://127.0.0.1:8002"


def _idem_server_alive() -> bool:
    """探测服务是否已启动（2 秒超时，不重试）。"""
    try:
        requests.get(BASE + "/accounts/1", timeout=2)
        return True
    except requests.RequestException:
        return False


# 服务没起就整组跳过 —— 而不是让 3 条用例报 ERROR（ERROR 会掩盖真正的问题）
pytestmark = pytest.mark.skipif(
    not _idem_server_alive(),
    reason='idem_server 未启动，先运行：python "D:\\大肥鱼\\学习\\07-异常与容错\\idem_server.py" 8002',
)


@pytest.fixture
def account():
    """每条用例前重置数据，保证隔离。"""
    requests.post(BASE + "/reset", timeout=5)
    return ApiClient(base_url=BASE)


def test_put_is_idempotent(account):
    """PUT 连发 3 次，余额始终 50，且最终状态也是 50。"""
    for _ in range(3):
        resp = account.put("/accounts/1", data={"balance": 50})
        assert resp.status_code == 200
        assert resp.json()["balance"] == 50.0

    # ③ 副作用只发生一次：回查真实状态
    assert account.get("/accounts/1").json()["balance"] == 50.0


def test_delete_is_idempotent(account):
    """DELETE 第一次 200，之后 404 —— 返回码变了，但最终状态一致，所以是幂等的。"""
    assert account.delete("/accounts/1").status_code == 200

    for _ in range(2):
        resp = account.delete("/accounts/1")
        assert resp.status_code == 404            # 返回码变了
        assert "不存在" in resp.json()["message"]  # 错误信息也要稳定

    # ② 状态一致：账户确实没了
    assert account.get("/accounts/1").status_code == 404


@pytest.mark.xfail(raises=AssertionError, strict=True,
                   reason="非幂等：POST 累加不可重试，重试会重复充值")
def test_post_deposit_is_not_idempotent(account):
    """POST 连发两次 → 余额 120 而不是 110。

    这条用例故意写成 xfail：它证明了「这个接口不能重试」。
    如果哪天后端把充值做成幂等（比如要求传幂等键），它会变成 XPASS，
    那时就该撤掉这个标记。
    """
    account.post("/accounts/1/deposit", data={"amount": 10})
    account.post("/accounts/1/deposit", data={"amount": 10})

    # 用户的期望是"只充一次" —— 实际充了两次，所以断言会失败 → xfailed
    assert account.get("/accounts/1").json()["balance"] == 110.0
