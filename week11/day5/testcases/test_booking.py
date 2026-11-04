import pytest
from common.schema_utils import assert_matches_schema
from conftest import load_yaml_file  # 导入普通读yaml函数

# 用例1：ping健康检查 smoke
@pytest.mark.network
@pytest.mark.api
@pytest.mark.booking
def test_ping(booking_api):
    resp = booking_api.ping()
    assert resp.status_code == 201

# 用例2：登录拿token正向 smoke
@pytest.mark.network
@pytest.mark.api
@pytest.mark.booking
def test_auth_get_token(booking_api):
    resp = booking_api.auth("admin", "password123")
    assert resp.status_code == 200
    assert "token" in resp.json()

# 用例3：yaml数据驱动 + schema校验 + 业务断言 smoke
@pytest.mark.network
@pytest.mark.api
@pytest.mark.booking
def test_create_booking_yaml(booking_api):
    # 直接调用普通函数读yaml，不用fixture注入
    case_data = load_yaml_file("data/booking_cases.yaml")
    happy_data = case_data["create_happy"]

    resp = booking_api.create_booking(**happy_data)
    assert resp.status_code == 200
    booking_id = resp.json()["bookingid"]

    # 查询刚创建的订单
    get_resp = booking_api.get_booking(booking_id)
    get_json = get_resp.json()

    # Schema 直接写在这里，不抽fixture
    booking_schema = {
        "type": "object",
        "properties": {
            "firstname": {"type": "string"},
            "lastname": {"type": "string"},
            "totalprice": {"type": "number"},
            "depositpaid": {"type": "boolean"},
            "bookingdates": {
                "type": "object",
                "properties": {
                    "checkin": {"type": "string"},
                    "checkout": {"type": "string"}
                },
                "required": ["checkin", "checkout"]
            },
            "additionalneeds": {"type": "string"}
        },
        "required": ["firstname","lastname","totalprice","depositpaid","bookingdates","additionalneeds"]
    }
    # 契约校验
    assert_matches_schema(get_json, booking_schema)
    # 业务断言：存进去的名字和提交的一样
    assert get_json["firstname"] == happy_data["firstname"]

# 用例4：参数化，负向：查询不存在id smoke
@pytest.mark.network
@pytest.mark.api
@pytest.mark.booking
@pytest.mark.parametrize("bid", [999999, 888888])
def test_get_booking_not_exist(booking_api, bid):
    resp = booking_api.get_booking(bid)
    assert resp.status_code == 404

# 用例5：负向：缺少必填字段
@pytest.mark.api
@pytest.mark.booking
def test_create_booking_missing_field(booking_api):
    case_data = load_yaml_file("data/booking_cases.yaml")
    bad_data = case_data["create_missing_lastname"]
    resp = booking_api.create_booking(**bad_data)
    assert resp.status_code in (400, 500)

# 用例6：负向：错误token删除
@pytest.mark.api
@pytest.mark.booking
def test_delete_with_fake_token(booking_api):
    fake_token = "fake123456"
    resp = booking_api.delete_booking(1, fake_token)
    assert resp.status_code in (401,403)

# 用例7：局部更新正向 smoke
@pytest.mark.network
@pytest.mark.api
@pytest.mark.booking
def test_partial_update(booking_api):
    # 自己在当前用例里面登录拿token，不用夹具
    auth_resp = booking_api.auth("admin", "password123")
    token = auth_resp.json()["token"]

    # 先建订单
    create_resp = booking_api.create_booking(
        "Lily", "Wang", 300, True, "2026-12-03", "2026-12-06", "Dinner"
    )
    bid = create_resp.json()["bookingid"]

    # 局部修改
    payload = {"additionalneeds": "No food"}
    update_resp = booking_api.partial_update_booking(bid, token, payload)
    assert update_resp.status_code == 200
    # 业务断言：修改后的内容正确
    after_get = booking_api.get_booking(bid).json()
    assert after_get["additionalneeds"] == "No food"

# 用例8：删除订单正向 smoke
@pytest.mark.network
@pytest.mark.api
@pytest.mark.booking
def test_delete_booking_success(booking_api):
    auth_resp = booking_api.auth("admin", "password123")
    token = auth_resp.json()["token"]

    create_resp = booking_api.create_booking(
        "Jack", "Li", 500, False, "2026-12-07", "2026-12-09", ""
    )
    bid = create_resp.json()["bookingid"]

    del_resp = booking_api.delete_booking(bid, token)
    assert del_resp.status_code == 201
    # 删完查不到
    get_resp = booking_api.get_booking(bid)
    assert get_resp.status_code == 404


# ══════════════════════════════════════════════════════════════════
# 用例9：PUT 全量更新正向（对比 PATCH）
# ══════════════════════════════════════════════════════════════════
@pytest.mark.network
@pytest.mark.api
@pytest.mark.booking
def test_put_full_update_success(booking_api):
    """PUT 全量替换：传完整字段 → 200，所有字段都被新值覆盖。"""
    token = booking_api.auth("admin", "password123").json()["token"]
    bid = booking_api.create_booking(
        "Sam", "Zhao", 100, False, "2026-12-20", "2026-12-22", "None"
    ).json()["bookingid"]

    new_payload = {
        "firstname": "Sammy",
        "lastname": "Zhao",
        "totalprice": 999,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-12-21", "checkout": "2026-12-25"},
        "additionalneeds": "Breakfast",
    }
    resp = booking_api.update_booking(bid, token, new_payload)
    assert resp.status_code == 200

    after = booking_api.get_booking(bid).json()
    assert after["firstname"] == "Sammy"
    assert after["totalprice"] == 999
    assert after["bookingdates"]["checkout"] == "2026-12-25"


# ══════════════════════════════════════════════════════════════════
# 用例10：PUT 只传部分字段 → 400，且数据不被改动
# ══════════════════════════════════════════════════════════════════
@pytest.mark.network
@pytest.mark.api
@pytest.mark.booking
def test_put_partial_payload_rejected_and_no_side_effect(booking_api):
    """PUT 语义是全量替换：只传 firstname 应被拒绝（400），且原数据保持不变。

    实测：PUT /booking/{id} {"firstname":"Tommy"} → 400，对象未被修改。
    对比 PATCH 同名 payload → 200 且只改 firstname（见 test_partial_update）。
    """
    token = booking_api.auth("admin", "password123").json()["token"]
    bid = booking_api.create_booking(
        "Tom", "Lee", 200, True, "2026-12-10", "2026-12-12", "Late"
    ).json()["bookingid"]

    resp = booking_api.update_booking(bid, token, {"firstname": "Tommy"})
    assert resp.status_code == 400

    after = booking_api.get_booking(bid).json()
    # 关键：失败的 PUT 不能留下部分写入（原子性）
    assert after["firstname"] == "Tom"
    assert after["lastname"] == "Lee"
