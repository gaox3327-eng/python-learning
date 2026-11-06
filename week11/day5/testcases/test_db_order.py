"""第 12 课：接口 + 数据库三层验证

依赖：
    1. 本地 MySQL（shop_test 库）
    2. python db_app.py 8010 已启动
"""

from decimal import Decimal

import pytest

from common.db_utils import query

pytestmark = pytest.mark.db


def test_create_order_deducts_stock_and_writes_rows(db_api, db):
    """下单三层验证：接口 → 主表 → 关联表。"""
    before = query(db, "SELECT stock FROM products WHERE id=1")

    resp = db_api.post("/orders", data={"user_id": 1, "product_id": 1, "qty": 3})
    assert resp.status_code == 201

    body = resp.json()
    order_id = body["order_id"]
    assert body["amount"] == "1197.00"

    # ① 库存真的少了 3
    assert query(db, "SELECT stock FROM products WHERE id=1") == before - 3

    # ② 主表真的插了，而且金额/用户正确
    assert query(db, "SELECT user_id FROM orders WHERE order_id=%s", (order_id,)) == 1
    assert query(db, "SELECT amount FROM orders WHERE order_id=%s", (order_id,)) == Decimal("1197.00")

    # ③ 明细真的写了
    assert query(db, "SELECT COUNT(*) FROM order_items WHERE order_id=%s", (order_id,)) == 1
    assert query(db, "SELECT qty FROM order_items WHERE order_id=%s", (order_id,)) == 3


def test_refund_updates_refunded_in_db(db_api, db):
    """退款后查库：refunded 真的变了。"""
    oid = db_api.post("/orders", data={"user_id": 2, "product_id": 3, "qty": 2}).json()["order_id"]

    assert query(db, "SELECT refunded FROM orders WHERE order_id=%s", (oid,)) == Decimal("0.00")

    resp = db_api.post("/refunds", data={"order_id": oid, "amount": 10})
    assert resp.status_code == 200

    assert query(db, "SELECT refunded FROM orders WHERE order_id=%s", (oid,)) == Decimal("10.00")


def test_failed_order_leaves_no_dirty_data(db_api, db):
    """预期失败的单：接口报错，库存必须没变（事务回滚）。"""
    before = query(db, "SELECT stock FROM products WHERE id=3")

    resp = db_api.post("/orders", data={"user_id": 999, "product_id": 3, "qty": 2})
    assert resp.status_code == 500          # 外键约束：user_id 不存在

    assert query(db, "SELECT stock FROM products WHERE id=3") == before


@pytest.mark.xfail(strict=True, reason="缺陷: 退款不校验累计金额，refunded 可以超过订单 amount")
def test_refund_cannot_exceed_order_amount(db_api, db):
    """已知缺陷：连退两次超额，接口都返回 200。"""
    oid = db_api.post("/orders", data={"user_id": 1, "product_id": 1, "qty": 1}).json()["order_id"]
    amount = query(db, "SELECT amount FROM orders WHERE order_id=%s", (oid,))

    db_api.post("/refunds", data={"order_id": oid, "amount": 5})
    db_api.post("/refunds", data={"order_id": oid, "amount": float(amount)})

    assert query(db, "SELECT refunded FROM orders WHERE order_id=%s", (oid,)) <= amount
