import pytest 
from common.api_client import ApiClient
from common.validators import assert_matches_schema
PRODUCTS_SCHEMA = {
    "type": "object",
    "properties": {
        "products": {"type": "array"},
        "total": {"type": "integer"},
        "skip": {"type": "integer"},
        "limit": {"type": "integer"}
    },
    "required": ["products", "total", "skip", "limit"]
}

def test_products_normal_list(dummy_client: ApiClient):
    """1、无参数正常查询商品列表，校验返回结构契约"""
    resp = anon_client.get("/products")
    assert resp.status_code == 200
    data = resp.json()
    assert_matches_schema(data, PRODUCTS_SCHEMA, label="商品列表返回结构")

def test_products_pagination_limit3(dummy_client: ApiClient):
    """2、分页 limit=3 skip=0，返回3条"""
    resp = anon_client.get("/products", params={"limit":3, "skip":0})
    assert resp.status_code == 200
    assert len(resp.json()["products"]) == 3

def test_products_sort_price_asc(dummy_client: ApiClient):
    """3、按价格升序排序"""
    resp = anon_client.get("/products", params={"sortBy":"price", "order":"asc"})
    assert resp.status_code == 200
    items = resp.json()["products"]
    prices = [p["price"] for p in items]
    assert prices == sorted(prices)  

@pytest.mark.parametrize("bad_limit", [-5, "abc"])
def test_products_bad_limit_param(dummy_client: ApiClient, bad_limit):
    """4、5 负向：limit传负数 / 非数字，返回400"""
    resp = anon_client.get("/products", params={"limit": bad_limit})
    assert resp.status_code == 400

def test_products_bad_order(dummy_client: ApiClient):
    """6、负向：order参数非法，不是asc/desc"""
    resp = anon_client.get("/products", params={"sortBy":"price", "order":"hhh"})
    assert resp.status_code == 400      

def test_products_select_nonexist_key(dummy_client: ApiClient):
    """7、边界：select不存在字段"""
    resp = anon_client.get("/products", params={"select":"xxxabc"})
    assert resp.status_code == 200
    item = resp.json()["products"][0]
    assert "xxxabc" not in item
