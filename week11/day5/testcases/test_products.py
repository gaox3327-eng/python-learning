"""独立作战测试：dummyjson.com/products
limit = 本次查询，想要拿多少条。
用例清单（10 个函数 / 20 个用例）：
    正向  1. 列表结构契约
          2. 分页 limit × 3
          3. 排序 asc/desc × 2
          4. 字段裁剪 select
          5. 单商品详情
    负向  6. limit 非法 × 2（-5 / abc）→ 400
          7. order 非法 → 400
          8. skip 负数 → 400
          9. 不存在的商品 id × 2（0 / 99999）→ 404
    边界 10. 搜索无结果 → 200 + 空数组
"""

import pytest

from common.validators import assert_matches_schema

from common.data_loader import load_cases


# ---------------------------------------------------------------- 契约
LIST_SCHEMA = {
    "type": "object",
    "required": ["products", "total", "skip", "limit"],
    "properties": {
        "products": {"type": "array"},
        "total": {"type": "integer", "minimum": 0},
        "skip": {"type": "integer", "minimum": 0},
        "limit": {"type": "integer", "minimum": 0},
    },
    "additionalProperties": False,
}

PRODUCT_SCHEMA = {
    "type": "object",
    "required": ["id", "title", "price"],
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "title": {"type": "string", "minLength": 1},
        "price": {"type": "number", "minimum": 0},
    },
}

ERROR_SCHEMA = {
    "type": "object",
    "required": ["message"],
    "properties": {"message": {"type": "string", "minLength": 1}},
    "additionalProperties": False,
}


INVALID_LIMIT = load_cases("products_cases.yaml", "invalid_limit")
NOT_FOUND = load_cases("products_cases.yaml", "not_found_id")

# ---------------------------------------------------------------- 正向
def test_list_contract(products_api):
    """1. 列表接口的结构必须符合契约"""
    resp = products_api.list_products()
    assert resp.status_code == 200
    assert_matches_schema(resp.json(), LIST_SCHEMA, "GET /products")


@pytest.mark.parametrize("limit", [1, 3, 10], ids=["limit1", "limit3", "limit10"])
def test_list_pagination(products_api, limit):
    """2. 分页：返回条数应等于 limit"""
    resp = products_api.list_products(limit=limit)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["products"]) == limit
    assert data["limit"] == limit


@pytest.mark.parametrize(
    "order, ascending", [("asc", True), ("desc", False)], ids=["asc", "desc"]
)
def test_list_sort_by_price(products_api, order, ascending):
    """3. 排序：asc 递增、desc 递减"""
    resp = products_api.list_products(sortBy="price", order=order, limit=10)
    assert resp.status_code == 200
    prices = [item["price"] for item in resp.json()["products"]]
    assert prices == sorted(prices, reverse=not ascending)


def test_list_select_fields(products_api):
    """4. 字段裁剪：select=title,price 时每条只含 id/title/price"""
    resp = products_api.list_products(select="title,price", limit=3)
    assert resp.status_code == 200
    for item in resp.json()["products"]:
        assert set(item.keys()) == {"id", "title", "price"}
        assert isinstance(item["title"], str)
        assert item["price"] >= 0


def test_get_product_ok(products_api):
    """5. 单商品详情：200 + 契约 + id 与请求一致（业务断言）"""
    resp = products_api.get_product(1)
    assert resp.status_code == 200

    data = resp.json()
    assert_matches_schema(data, PRODUCT_SCHEMA, "GET /products/1")
    assert data["id"] == 1


# ---------------------------------------------------------------- 负向
@pytest.mark.parametrize("bad_limit", [-5, "abc"], ids=["negative", "not_a_number"])
def test_list_limit_invalid(products_api, bad_limit):
    """6. limit 为负数或非数字 → 400 + 错误信息契约"""
    resp = products_api.list_products(limit=bad_limit)
    assert resp.status_code == 400
    assert_matches_schema(resp.json(), ERROR_SCHEMA, "limit 非法")


def test_list_order_invalid(products_api):
    """7. order 不是 asc/desc → 400"""
    resp = products_api.list_products(sortBy="price", order="hhh")
    assert resp.status_code == 400
    assert_matches_schema(resp.json(), ERROR_SCHEMA, "order 非法")


def test_list_skip_negative(products_api):
    """8. skip 为负数 → 400"""
    resp = products_api.list_products(skip=-1)
    assert resp.status_code == 400
    assert_matches_schema(resp.json(), ERROR_SCHEMA, "skip 非法")


@pytest.mark.parametrize("product_id", [0, 99999], ids=["id0", "id99999"])
def test_get_product_not_found(products_api, product_id):
    """9. 不存在的商品 → 404 + 错误信息契约"""
    resp = products_api.get_product(product_id)
    assert resp.status_code == 404
    assert_matches_schema(resp.json(), ERROR_SCHEMA, "商品不存在")


# ---------------------------------------------------------------- 边界
def test_search_no_result(products_api):
    """10. 搜索无结果 → 200 + 空数组（不是 404）"""
    resp = products_api.search_products("zzzzzzzzzz")
    assert resp.status_code == 200

    data = resp.json()
    assert data["products"] == []
    assert data["total"] == 0

@pytest.mark.parametrize(
    "case",
    INVALID_LIMIT,
    ids=[c["id"] for c in INVALID_LIMIT],      # 用例名取自数据里的 id
)
def test_list_limit_invalid(products_api, case):
    resp = products_api.list_products(**case["params"])
    assert resp.status_code == case["expected_status"]


@pytest.mark.parametrize("case", NOT_FOUND, ids=[c["id"] for c in NOT_FOUND])
def test_get_product_not_found(products_api, case):
    resp = products_api.get_product(case["product_id"])
    assert resp.status_code == case["expected_status"]