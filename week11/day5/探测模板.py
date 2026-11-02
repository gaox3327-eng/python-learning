"""第 8 课 探测模板 —— 只发请求、只打印，不含断言。

用法：
    python 探测模板.py            # 需要先启动 server.py 8001

规则：
    1. 不许看 server.py 的源码（那是答案）
    2. **每个区块先写「期望」，再看打印结果**
    3. 发现不一致 = 一个缺陷候选，记进 bug 报告
"""

import requests

B = "http://127.0.0.1:8001"


def reset():
    requests.post(B + "/reset", timeout=5)


def probe(label, method, path, **kw):
    """发一次请求，打印状态码 + 关键字段。"""
    r = requests.request(method, B + path, timeout=5, **kw)
    try:
        body = r.json()
    except Exception:
        body = r.text[:100]
    print(f"  {label:34s} {r.status_code}  {str(body)[:150]}")
    return r


# ══════════════════════════════════════════════════════════
# 一、正常路径：先把"应该是什么"想清楚
# ══════════════════════════════════════════════════════════
print("=== 1. 正常路径 ===")
reset()

# 商品 1：机械键盘，单价 399.0，库存 10
# 期望：GET /products/1 → 200，字段 id/name/price/stock 齐全
probe("商品1 详情", "GET", "/products/1")

# 期望：下单 3 件 → 201，返回 order_id 和 total
# 期望 total = 399.0 × 3 = 1197.0
# 期望 下单后 GET /products/1 的 stock = 10 - 3 = 7
r = probe("下单 qty=3", "POST", "/orders", json={"product_id": 1, "qty": 3})
print("         ↑ 记下 order_id：", r.json().get("order_id"))
probe("下单后商品1（期望 stock=7）", "GET", "/products/1")

# 期望：查这个订单 → 200，qty=3，refunded=0.0
# probe("查订单", "GET", f"/orders/{你记下的 order_id}")


# ══════════════════════════════════════════════════════════
# 二、边界：0 / 1 / 刚好超过
# ══════════════════════════════════════════════════════════
print("\n=== 2. 边界 ===")
reset()

# 期望：买 1 件 → 201，stock = 10 - 1 = 9
probe("下单 qty=1", "POST", "/orders", json={"product_id": 1, "qty": 1})
probe("下单后商品1（期望 stock=9）", "GET", "/products/1")

# 期望：买 0 件 → 400（数量必须大于 0）
probe("下单 qty=0", "POST", "/orders", json={"product_id": 1, "qty": 0})

# 期望：买负数 → 400
probe("下单 qty=-1", "POST", "/orders", json={"product_id": 1, "qty": -1})

# 期望：把库存清空——商品 3 库存 5，买 5 件 → 201，stock = 0
probe("商品3 买光（库存5）", "POST", "/orders", json={"product_id": 3, "qty": 5})
probe("商品3 买光后（期望 stock=0）", "GET", "/products/3")


# ══════════════════════════════════════════════════════════
# 三、业务规则缺失：库存不够还买呢？
# ══════════════════════════════════════════════════════════
print("\n=== 3. 超卖检查 ===")
reset()

# 期望：只有 5 件却买 99 件 → 应该拒绝（400）
# 关键：买完再看库存，库存**绝不能是负数**
probe("商品3 库存5，买99", "POST", "/orders", json={"product_id": 3, "qty": 99})
probe("买完后商品3（stock 是否负数？）", "GET", "/products/3")


# ══════════════════════════════════════════════════════════
# 四、分页：翻页会不会重/漏
# ══════════════════════════════════════════════════════════
print("\n=== 4. 分页 ===")
reset()

# 共 8 个商品。期望：
#   offset=0, limit=3 → id 1,2,3
#   offset=3, limit=3 → id 4,5,6     ← 重点看这里
#   offset=6, limit=3 → id 7,8
for off in (0, 3, 6):
    r = probe(f"offset={off} limit=3", "GET", f"/products?offset={off}&limit=3")
    print("         ↑ 拿到的 id：", [i["id"] for i in r.json().get("items", [])])

# 期望：offset 为负数 → 400
probe("offset=-1", "GET", "/products?offset=-1&limit=3")
# 期望：limit=0 → 400（或至少不该返回全部）
probe("limit=0", "GET", "/products?offset=0&limit=0")


# ══════════════════════════════════════════════════════════
# 五、安全：登录会不会被绕过
# ══════════════════════════════════════════════════════════
print("\n=== 5. 登录 ===")
reset()

# 已知账号：alice / alice123
# 期望：正确密码 → 200 + token
probe("登录（正确密码）", "POST", "/login", json={"username": "alice", "password": "alice123"})
# 期望：错误密码 → 401
probe("登录（错误密码）", "POST", "/login", json={"username": "alice", "password": "WRONG"})
# 期望：不传密码 → 401
probe("登录（不传密码）", "POST", "/login", json={"username": "alice"})
# 期望：用户名不存在 → 401
probe("登录（用户不存在）", "POST", "/login", json={"username": "bob", "password": "x"})


# ══════════════════════════════════════════════════════════
# 六、金额精度：小数累加
# ══════════════════════════════════════════════════════════
print("\n=== 6. 金额精度 ===")
reset()

# 商品 4：USB 集线器，单价 0.1
# 期望：买 3 件 → total 应该正好是 0.3
r = probe("商品4 单价0.1 买3件", "POST", "/orders", json={"product_id": 4, "qty": 3})
total = r.json().get("total")
print(f"         ↑ total = {total!r}   是否等于 0.3：{total == 0.3}")

# 商品 2：无线鼠标，单价 19.99
# 期望：买 2 件 → total = 39.98
probe("商品2 单价19.99 买2件", "POST", "/orders", json={"product_id": 2, "qty": 2})


# ══════════════════════════════════════════════════════════
# 七、退款：能不能超退
# ══════════════════════════════════════════════════════════
print("\n=== 7. 退款 ===")
reset()

r = probe("买 1 件鼠标（总额9.9）", "POST", "/orders", json={"product_id": 5, "qty": 1})
oid = r.json().get("order_id")

# 期望：退 5 元 → 200，refunded_total = 5
probe("退 5 元", "POST", "/refunds", json={"order_id": oid, "amount": 5})
# 期望：再退 5 元 → 累计 10，但订单总额只有 9.9 → **应该拒绝**
probe("再退 5 元（累计会超过9.9）", "POST", "/refunds", json={"order_id": oid, "amount": 5})
# 期望：退 0 / 负数 → 400
probe("退 0 元", "POST", "/refunds", json={"order_id": oid, "amount": 0})

print("\n完成。把每一处「期望 ≠ 实际」记下来，那些就是缺陷。")
