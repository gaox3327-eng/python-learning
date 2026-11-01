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

    # ③ 格式：响应必须是 JSON（能区分「业务 404 的 JSON」和「路由 404 的 HTML」）
    content_type = resp.headers.get("Content-Type", "")
    assert "application/json" in content_type, (
        f"{case['id']}: 期望 JSON，实际 Content-Type={content_type!r}"
    )

    # ④ 错误体结构：只对 4xx/5xx 生效
    #    200 的响应体是业务数据（products 列表），没有 message —— 不能无条件断言
    body = resp.json()
    if resp.status_code >= 400:
        assert isinstance(body.get("message"), str) and body["message"].strip(), (
            f"{case['id']}: 错误体缺少非空 message，实际 {body}"
        )
    else:
        assert body, f"{case['id']}: 成功响应体不应为空"
