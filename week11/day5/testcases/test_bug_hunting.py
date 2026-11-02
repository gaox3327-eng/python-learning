"""第 8 课：抓 bug 实战 —— 6 条缺陷用例

每条都标 xfail(strict=True)：
    缺陷存在   → 断言失败 → xfailed（正常）
    缺陷被修好 → 断言通过 → XPASS(strict) → FAILED（提醒撤掉标记）

依赖 conftest 的 shop 夹具（自动启用 8001 服务 + 每条用例前 /reset）。
"""

import pytest


# ══════════════════════════════════════════════════════════════════
# BUG-01 安全：登录不校验密码
# ══════════════════════════════════════════════════════════════════
@pytest.mark.xfail(strict=True, reason="缺陷: POST /login 不校验密码，错密码也签发 token")
def test_login_rejects_wrong_password(shop):
    resp = shop.post("/login", data={"username": "alice", "password": "WRONG"})

    # 期望：凭据错误 → 401，且不返回 token
    assert resp.status_code == 401, f"错密码竟然登录成功：{resp.json()}"
    assert "token" not in resp.json()


# ══════════════════════════════════════════════════════════════════
# BUG-02 业务规则：退款可超过订单总额
# ══════════════════════════════════════════════════════════════════
@pytest.mark.xfail(strict=True, reason="缺陷: POST /refunds 不校验累计退款是否超过订单总额")
def test_refund_cannot_exceed_order_total(shop):
    # 商品 5 单价 9.9，买 1 件 → 订单总额 9.9
    order = shop.post("/orders", data={"product_id": 5, "qty": 1}).json()
    order_id = order["order_id"]
    total = order["total"]

    first = shop.post("/refunds", data={"order_id": order_id, "amount": 5})
    assert first.status_code == 200

    # 再退 5 元 → 累计 10 > 总额 9.9，应当拒绝
    second = shop.post("/refunds", data={"order_id": order_id, "amount": 5})
    assert second.status_code in (400, 409), (
        f"累计退款 {second.json().get('refunded_total')} 已超过订单总额 {total}"
    )


# ══════════════════════════════════════════════════════════════════
# BUG-03 数值计算：库存少扣 1
# ══════════════════════════════════════════════════════════════════
@pytest.mark.xfail(strict=True, reason="缺陷: 下单后库存扣减少 1（10-3 得 8，应得 7）")
def test_stock_deducted_exactly(shop):
    before = shop.get("/products/1").json()["stock"]        # 10
    shop.post("/orders", data={"product_id": 1, "qty": 3})
    after = shop.get("/products/1").json()["stock"]

    assert after == before - 3, f"库存应 {before - 3}，实际 {after}"


# ══════════════════════════════════════════════════════════════════
# BUG-04 业务规则 + 状态一致性：允许超卖，库存变负
# ══════════════════════════════════════════════════════════════════
@pytest.mark.xfail(strict=True, reason="缺陷: 库存不足仍可下单，导致库存为负数（超卖）")
def test_cannot_oversell(shop):
    stock = shop.get("/products/3").json()["stock"]          # 5
    resp = shop.post("/orders", data={"product_id": 3, "qty": stock + 99})

    # 期望：库存不足 → 拒绝
    assert resp.status_code in (400, 409), f"库存 {stock} 却接受了 {stock + 99} 件"

    # 再确认库存绝不为负
    assert shop.get("/products/3").json()["stock"] >= 0


# ══════════════════════════════════════════════════════════════════
# BUG-05 分页：偏移错位
# ══════════════════════════════════════════════════════════════════
@pytest.mark.xfail(strict=True, reason="缺陷: 分页 offset 少算 1，第二页数据错位")
def test_pagination_offset_not_shifted(shop):
    items = shop.get("/products", params={"offset": 3, "limit": 3}).json()["items"]
    ids = [item["id"] for item in items]

    assert ids == [4, 5, 6], f"offset=3 应返回 4,5,6，实际 {ids}"


# ══════════════════════════════════════════════════════════════════
# BUG-06 金额精度：float 累加丢精度
# ══════════════════════════════════════════════════════════════════
@pytest.mark.xfail(strict=True, reason="缺陷: 金额用 float 累加，0.1×3 得不到 0.3")
def test_amount_has_no_float_error(shop):
    # 商品 4 单价 0.1，买 3 件
    total = shop.post("/orders", data={"product_id": 4, "qty": 3}).json()["total"]

    assert total == 0.3, f"0.1×3 应等于 0.3，实际 {total!r}"
