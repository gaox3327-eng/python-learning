"""第 14 课：本地"假 LLM"，用来练评测（不需要任何 API key）

它模拟真实大模型的三件事：
    1. temperature=0 时完全确定；>0 时同问不同答（随机改写）
    2. 三种行为模式：正常 / 格式不合规 / 幻觉（编造事实）

用法：
    from fake_llm import ask
    ask("退款 100 元要多久到账？")                      # 正常
    ask("...", temperature=0.8, seed=1)                 # 带随机
    ask("...", mode="flaky_format")                     # 模拟格式违规
    ask("...", mode="hallucinate")                      # 模拟幻觉

命令行自测：
    python fake_llm.py
"""

import json
import random

# ── 知识库（"模型会背下来的事实"）
FACTS = {
    "退款": "退款通常在 1-3 个工作日到账，具体以银行处理时间为准。",
    "库存": "库存会在下单成功后立即扣减，售罄后无法下单。",
    "发票": "电子发票会在订单完成后 24 小时内发送到注册邮箱。",
    "运费": "单笔订单满 99 元免运费，否则收取 10 元运费。",
}

# 语气词 / 同义替换，用来模拟"温度带来的多样性"
PREFIXES = ["", "好的，", "简单说，", "根据我们的规则，"]
SUFFIXES = ["", " 如有疑问可联系客服。", " 希望有帮助。"]
SYNONYMS = [("通常", "一般"), ("立即", "马上"), ("无法", "不能")]


def _base_answer(prompt: str) -> str:
    for key, answer in FACTS.items():
        if key in prompt:
            return answer
    return "这个问题我暂时没有相关信息。"


def _apply_temperature(text: str, temperature: float, rng: random.Random) -> str:
    """temperature>0 时做随机改写：同问不同答。"""
    if temperature <= 0:
        return text
    if rng.random() < min(temperature, 1.0):
        text = rng.choice(PREFIXES) + text
    if rng.random() < temperature * 0.6:
        text = text + rng.choice(SUFFIXES)
    if rng.random() < temperature * 0.5:
        for old, new in SYNONYMS:
            if old in text:
                text = text.replace(old, new, 1)
                break
    return text.strip()


def ask(prompt: str, temperature: float = 0.0, seed: int | None = None,
        mode: str = "good") -> str:
    """一次"模型调用"。

    mode:
        good          正常
        flaky_format  返回带了多余解释的文本（本该是纯 JSON）
        hallucinate   编造一个不存在的政策
    """
    rng = rng0 = random.Random(seed) if seed is not None else random.Random()

    if mode == "hallucinate":
        return "根据我们的政策，退款会额外补偿 50 元现金券，并且 24 小时内到账。"

    if mode == "flaky_format":
        # 本该输出 JSON，却加了自然语言前缀
        payload = {"intent": "refund", "amount": 100}
        return f"好的，这是结果：{json.dumps(payload, ensure_ascii=False)} 希望有帮助！"

    return _apply_temperature(_base_answer(prompt), temperature, rng0)


def ask_json(prompt: str, **kw) -> str:
    """要求模型输出 JSON 的场景（真实项目里常用）。"""
    return ask(prompt, **kw)


if __name__ == "__main__":
    print("--- 温度 0（确定）---")
    for _ in range(3):
        print("  ", ask("退款要多久到账？"))
    print("--- 温度 0.9（同问不同答）---")
    for i in range(3):
        print("  ", ask("退款要多久到账？", temperature=0.9, seed=i))
    print("--- 格式违规 ---")
    print("  ", ask("提取退款信息", mode="flaky_format"))
    print("--- 幻觉 ---")
    print("  ", ask("退款政策是什么？", mode="hallucinate"))
