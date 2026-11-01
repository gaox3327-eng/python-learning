"""第 7 课 Day 3：错误码矩阵

数据在 data/error_matrix.yaml，代码只负责「分发 + 三层断言」。
新增场景只改 yaml，不改这里。

两类用例：
    params 类 → GET /products?<params>
    path  类 → <method> <path>
"""

import pytest

from api.products_api import DUMMY_BASE
from common.api_client import ApiClient
from common.data_loader import load_cases

MATRIX = load_cases("error_matrix.yaml", "error_matrix")

# 用 pytest.param 承载"这条是已知缺陷"的标记：
#   断言照常执行 —— 缺陷还在时失败 → xfailed
#   缺陷被修好时通过   → XPASS(strict) 变成 FAILED，提醒你撤掉标记
PARAMS = [
    pytest.param(
        case,
        id=case["id"],
        marks=pytest.mark.xfail(strict=True, reason=case.get("desc", "已知缺陷")),
    )
    if case.get("known_defect")
    else pytest.param(case, id=case["id"])
    for case in MATRIX
]


@pytest.fixture
def fast_client():
    """矩阵专用客户端：短超时 + 少量重试。

    实测 dummyjson 基线 1~6 秒、偶发几十秒（SSL 握手超时），
    所以 5 秒 + 0 重试会必然 flaky；这里折中成 10 秒 + 1 次重试。
    （真正该用「极短超时 + 0 重试」的是第 8 课的本地 mock 服务。）
    """
    return ApiClient(base_url=DUMMY_BASE, timeout=10, retries=1)


@pytest.mark.parametrize("case", PARAMS)
def test_error_matrix(fast_client, case):
    # ① 发请求：按数据决定用参数还是路径
    if "path" in case:
        resp = fast_client.request(
            case.get("method", "GET"),
            case["path"],
            params=case.get("params") or None,
        )
    else:
        resp = fast_client.get("/products", params=case["params"])

    # ② 状态码
    assert resp.status_code == case["expected_status"], (
        f"{case['id']}: 期望 {case['expected_status']}，实际 {resp.status_code}，"
        f"响应前 80 字 {resp.text[:80]!r}"
    )

    # ③ 格式：由数据声明期望的 Content-Type（默认 JSON）
    #    这样「业务 404 → JSON」和「路由 404 → HTML」都能被精确表达
    expected_ct = case.get("expected_content_type", "application/json")
    actual_ct = resp.headers.get("Content-Type", "")
    assert expected_ct in actual_ct, (
        f"{case['id']}: 期望 Content-Type 含 {expected_ct!r}，实际 {actual_ct!r}"
    )

    # ④ 体结构：只有 JSON 才做结构断言（HTML 错误页没有 JSON 体，不能硬套）
    if "application/json" in actual_ct:
        body = resp.json()
        if resp.status_code >= 400:
            assert isinstance(body.get("message"), str) and body["message"].strip(), (
                f"{case['id']}: 错误体缺少非空 message，实际 {body}"
            )
        else:
            assert body, f"{case['id']}: 成功响应体不应为空"


#单独写「业务 404（JSON）」和「路由 404（HTML）」两条

def test_business_404_returns_json(fast_client):
    resp = fast_client.get("/products/99999")

    assert resp.status_code == 404
    assert "application/json" in resp.headers["Content-Type"]
    assert "not found" in resp.json()["message"]


def test_route_404_returns_html_today(fast_client):
    """路由 404：路径不存在 → 框架默认 HTML 错误页。

    这条**钉住现状**（绿色通过），用来说明两种 404 的区别。
    实测：GET /productsx → 404 + text/html
    """
    resp = fast_client.get("/productsx")

    assert resp.status_code == 404
    assert "text/html" in resp.headers["Content-Type"]     # ← 就是这里不一样


@pytest.mark.xfail(strict=True, reason="缺陷: 路由 404 返回 HTML，破坏 JSON 契约")
def test_route_404_should_be_json(fast_client):
    """同一位置，但按**契约**期望 JSON —— 所以它是缺陷（xfail）。

    和上一条的区别：
        上一条：记录"现在是什么"（绿）
        这一条：坚持"应该是什么"（黄）
    """
    resp = fast_client.get("/productsx")

    assert resp.status_code == 404
    assert "application/json" in resp.headers["Content-Type"]