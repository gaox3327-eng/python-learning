"""第 15 课：本地"假 Agent"（不需要 API key）

和 LLM 的关键区别：
    LLM    只返回一段文本
    Agent  返回「决策过程」：调了哪些工具、参数是什么、顺序如何、几步结束

用法：
    from fake_agent import run
    r = run("查一下订单 1001 的状态")
    r["answer"]    -> 最终回复
    r["steps"]     -> [{"tool": "get_order", "args": {"order_id": 1001}}, ...]
    r["finished"]  -> 是否在步数上限内结束

缺陷模式（用来验证你的断言能不能抓到问题）：
    good          正常
    wrong_tool    调用黑名单工具（越权）
    too_many      反复调用同一工具（低效）
    skip_check    不查订单直接退款（跳步）
    hallucinate   不调工具，直接编答案
"""

import re

# 白名单工具
TOOLS = {
    "get_order": {"required": ["order_id"]},
    "get_product": {"required": ["product_id"]},
    "create_refund": {"required": ["order_id", "amount"]},
    "send_email": {"required": ["to", "subject"]},
}

# 黑名单工具：绝不允许
FORBIDDEN_TOOLS = {"drop_database", "delete_all_orders", "export_all_users"}

ORDERS = {
    1001: {"order_id": 1001, "user_id": 1, "amount": 1197.00, "refunded": 0.0, "status": "paid"},
    1002: {"order_id": 1002, "user_id": 2, "amount": 1299.00, "refunded": 0.0, "status": "paid"},
}
PRODUCTS = {1: {"id": 1, "stock": 10, "price": 399.0}, 2: {"id": 2, "stock": 5, "price": 1299.0}}


def _step(tool, **args):
    return {"tool": tool, "args": args}


def _digits(text: str) -> list[int]:
    return [int(m) for m in re.findall(r"\d+", text)]


def _pick_order_id(task: str, default: int = 1001) -> int:
    """从任务里找 4~5 位订单号（1001 / 1002 / 9999 ...）。"""
    for n in _digits(task):
        if 1000 <= n <= 99999:
            return n
    return default


def _pick_product_id(task: str) -> int:
    """从任务里找"商品N"，找不到默认 1。"""
    m = re.search(r"商品\s*(\d+)", task)
    return int(m.group(1)) if m else 1


def _refund_amount(task: str, order_id: int) -> float | None:
    """从"退 X 元"里取金额；跳过订单号本身。"""
    for n in _digits(task):
        if n != order_id and n > 0:
            return float(n)
    return None


def _run(task: str, mode: str = "good", max_steps: int = 6) -> dict:
    # ── 缺陷模式：不调工具直接编
    if mode == "hallucinate":
        return {"task": task, "steps": [], "answer": "订单已退款成功，请查收。", "finished": True}

    # ── 缺陷模式：越权调用黑名单工具
    if mode == "wrong_tool":
        return {"task": task,
                "steps": [_step("get_order", order_id=1001), _step("drop_database")],
                "answer": "已处理好。", "finished": True}

    # ── 危险请求：拒绝，且不调任何工具
    if any(k in task for k in ("删除所有", "清空", "所有用户", "群发", "导出所有")):
        return {"task": task, "steps": [],
                "answer": "抱歉，这个操作超出我的权限范围，请联系管理员。", "finished": True}

    # ── 无关问题：不调工具
    if any(k in task for k in ("天气", "股票", "写诗", "笑话")):
        return {"task": task, "steps": [], "answer": "这个问题我无法回答。", "finished": True}

    # ── 退款类
    if "退" in task:
        order_id = _pick_order_id(task)
        order = ORDERS.get(order_id)
        steps = [_step("get_order", order_id=order_id)]

        if order is None:
            return {"task": task, "steps": steps,
                    "answer": f"订单 {order_id} 不存在，无法退款。", "finished": True}

        amount = _refund_amount(task, order_id) or 5.0

        if amount > order["amount"]:
            return {"task": task, "steps": steps,
                    "answer": f"退款金额 {amount:.0f} 超过订单金额 {order['amount']:.0f}，无法退款。",
                    "finished": True}

        if mode == "skip_check":
            return {"task": task,
                    "steps": [_step("create_refund", order_id=order_id, amount=amount)],
                    "answer": "已全额退款。", "finished": True}

        steps.append(_step("create_refund", order_id=order_id, amount=amount))
        return {"task": task, "steps": steps,
                "answer": f"订单 {order_id} 已退款 {amount:g} 元，1-3 个工作日到账。",
                "finished": True}

    # ── 查库存
    if "库存" in task:
        pid = _pick_product_id(task)
        steps = [_step("get_product", product_id=pid)]
        p = PRODUCTS.get(pid, {"stock": 0})
        return {"task": task, "steps": steps,
                "answer": f"商品 {pid} 当前库存 {p['stock']} 件。", "finished": True}

    # ── 查订单
    if "订单" in task:
        order_id = _pick_order_id(task)
        o = ORDERS.get(order_id)
        steps = [_step("get_order", order_id=order_id)]
        if o is None:
            return {"task": task, "steps": steps,
                    "answer": f"订单 {order_id} 不存在。", "finished": True}
        return {"task": task, "steps": steps,
                "answer": f"订单 {order_id} 金额 {o['amount']:g} 元，状态 {o['status']}。",
                "finished": True}

    return {"task": task, "steps": [], "answer": "请说得具体一些。", "finished": True}


def run(task: str, mode: str = "good", max_steps: int = 6) -> dict:
    """对外入口：先跑正常逻辑，再按 mode 施加缺陷。"""
    result = _run(task, mode=mode, max_steps=max_steps)

    if mode == "too_many":
        seed = result["steps"][0] if result["steps"] else _step("get_order", order_id=1001)
        result["steps"] = [dict(seed) for _ in range(max_steps)]
        result["finished"] = False

    return result


if __name__ == "__main__":
    for t in ["查订单 1001 的状态", "商品 2 的库存还有多少？", "给订单 1001 退 5 元",
              "给订单1001退2000元", "查不存在的订单 9999", "删除所有订单", "今天天气怎么样"]:
        r = run(t)
        print(f"{t:22s} -> {[s['tool'] for s in r['steps']]}")
        print(f"{'':22s}    {r['answer'][:46]}")
