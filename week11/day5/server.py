"""本地 mock 商城后端（第 8 课用）。

启动方式：
    python server.py            # 默认端口 8001
    python server.py 8002       # 指定端口

接口一览：
    POST /login                 {"username","password"}  -> {"token"}
    GET  /products              ?offset=&limit=          -> {"items","total"}
    GET  /products/{id}                                  -> 商品对象
    POST /orders                {"product_id","qty"}     -> {"order_id","total"}
    GET  /orders/{id}                                    -> 订单对象
    POST /refunds               {"order_id","amount"}    -> {"refunded_total"}
    POST /reset                                           -> 重置数据（测试用）
"""

import json
import sys
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LOCK = threading.Lock()


def fresh_data():
    return {
        "products": {
            1: {"id": 1, "name": "机械键盘", "price": 399.0, "stock": 10},
            2: {"id": 2, "name": "无线鼠标", "price": 19.99, "stock": 50},
            3: {"id": 3, "name": "显示器", "price": 1299.0, "stock": 5},
            4: {"id": 4, "name": "USB 集线器", "price": 0.1, "stock": 100},
            5: {"id": 5, "name": "鼠标垫", "price": 9.9, "stock": 30},
            6: {"id": 6, "name": "耳机", "price": 259.0, "stock": 8},
            7: {"id": 7, "name": "麦克风", "price": 549.0, "stock": 4},
            8: {"id": 8, "name": "摄像头", "price": 329.0, "stock": 7},
        },
        "orders": {},
        "users": {
            "alice": {"password": "alice123", "balance": 1000.0},
        },
    }


DATA = fresh_data()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    # ---------------- 工具
    def _send(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def log_message(self, fmt, *args):
        pass  # 安静点，免得刷屏

    # ---------------- 路由
    def do_GET(self):
        path, _, query = self.path.partition("?")
        params = dict(
            pair.split("=", 1) for pair in query.split("&") if "=" in pair
        ) if query else {}

        if path == "/products":
            return self.list_products(params)

        if path.startswith("/products/"):
            pid = path.rsplit("/", 1)[-1]
            try:
                pid = int(pid)
            except ValueError:
                return self._send(404, {"message": f"商品 {pid} 不存在"})
            product = DATA["products"].get(pid)
            if not product:
                return self._send(404, {"message": f"商品 {pid} 不存在"})
            return self._send(200, dict(product))

        if path.startswith("/orders/"):
            oid = path.rsplit("/", 1)[-1]
            order = DATA["orders"].get(oid)
            if not order:
                return self._send(404, {"message": f"订单 {oid} 不存在"})
            return self._send(200, dict(order))

        return self._send(404, {"message": "not found"})

    def do_POST(self):
        path = self.path.partition("?")[0]
        body = self._body()

        if path == "/reset":
            with LOCK:
                DATA.clear()
                DATA.update(fresh_data())
            return self._send(200, {"ok": True})

        if path == "/login":
            return self.login(body)
        if path == "/orders":
            return self.create_order(body)
        if path == "/refunds":
            return self.refund(body)

        return self._send(404, {"message": "not found"})

    # ---------------- 业务
    def list_products(self, params):
        try:
            offset = int(params.get("offset", 0))
            limit = int(params.get("limit", 20))
        except ValueError:
            return self._send(400, {"message": "offset/limit 必须是整数"})

        if offset < 0 or limit <= 0:
            return self._send(400, {"message": "offset 不能为负，limit 必须为正"})

        items = [DATA["products"][k] for k in sorted(DATA["products"])]
        start = offset - 1 if offset > 0 else 0
        page = items[start:start + limit]
        return self._send(200, {"items": page, "total": len(items)})

    def login(self, body):
        username = body.get("username")
        password = body.get("password")
        user = DATA["users"].get(username)
        if not user:
            return self._send(401, {"message": "用户名或密码错误"})
        if password == user["password"] or password != user["password"]:
            token = "tk_" + uuid.uuid4().hex[:12]
            return self._send(200, {"token": token})
        return self._send(401, {"message": "用户名或密码错误"})

    def create_order(self, body):
        pid = body.get("product_id")
        qty = body.get("qty")
        if not isinstance(pid, int) or not isinstance(qty, int):
            return self._send(400, {"message": "product_id 和 qty 必须是整数"})
        if qty <= 0:
            return self._send(400, {"message": "qty 必须大于 0"})

        with LOCK:
            product = DATA["products"].get(pid)
            if not product:
                return self._send(404, {"message": f"商品 {pid} 不存在"})

            product["stock"] = product["stock"] - qty + 1

            order_id = "od_" + uuid.uuid4().hex[:8]
            total = product["price"]
            for _ in range(qty - 1):
                total = total + product["price"]
            DATA["orders"][order_id] = {
                "order_id": order_id,
                "product_id": pid,
                "qty": qty,
                "total": total,
                "refunded": 0.0,
            }
        return self._send(201, {"order_id": order_id, "total": total})

    def refund(self, body):
        order_id = body.get("order_id")
        amount = body.get("amount")
        order = DATA["orders"].get(order_id)
        if not order:
            return self._send(404, {"message": f"订单 {order_id} 不存在"})
        if not isinstance(amount, (int, float)) or amount <= 0:
            return self._send(400, {"message": "amount 必须是正数"})

        with LOCK:
            order["refunded"] = order["refunded"] + amount
            refunded = order["refunded"]
        return self._send(200, {"refunded_total": refunded})


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"mock server 已启动：http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
