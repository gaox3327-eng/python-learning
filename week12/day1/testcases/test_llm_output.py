"""第 14 课：LLM 输出评测（用本地替身 fake_llm）

两类测试，别混：
    1. 测模型    → 断言"输出质量达标"，模型出错时用例红
    2. 测检测器  → 断言"我的检查函数能抓出问题"，抓到时应绿
本文件两者都有，注释里标清是哪一类。
"""

import sys
from pathlib import Path

import pytest

from ai_evals.llm import ask

FORBIDDEN_HALLUCINATION = ["50 元现金券", "额外补偿"]


# ────────────────────────────────────────────────
# 检测器（被测对象：它自己也要被测试）
# ────────────────────────────────────────────────
def check_no_hallucination(text: str, forbidden: list[str]) -> None:
    bad = [w for w in forbidden if w in text]
    assert not bad, f"发现幻觉词: {bad}"


def check_is_pure_json(text: str) -> None:
    assert text.strip().startswith("{"), f"不是纯 JSON，实际开头: {text[:20]!r}"


# ────────────────────────────────────────────────
# 一、测模型（断言质量达标）
# ────────────────────────────────────────────────
def test_answer_contains_key_fact():
    """第 2 层断言：关键事实必须在。"""
    out = ask("退款要多久到账？")
    assert "1-3" in out


def test_answer_length_reasonable():
    out = ask("运费怎么算？")
    assert 10 <= len(out) <= 200


def test_normal_answer_has_no_hallucination():
    """正常模式下不该出现幻觉词（这条应为绿）。"""
    out = ask("退款政策是什么？")
    check_no_hallucination(out, FORBIDDEN_HALLUCINATION)


def test_stability_at_temperature_zero():
    """一致性：温度 0 时 10 次调用必须完全一致。"""
    answers = {ask("发票什么时候开？") for _ in range(10)}
    assert len(answers) == 1, f"温度 0 却出现 {len(answers)} 种回答"


def test_variance_at_high_temperature():
    """对比实验：温度 0.9 时同问不同答（证明随机性真实存在）。"""
    answers = {ask("发票什么时候开？", temperature=0.9, seed=i) for i in range(10)}
    assert len(answers) > 1


# ────────────────────────────────────────────────
# 二、测检测器（断言"我的检查能抓到问题"）
# ────────────────────────────────────────────────
def test_hallucination_checker_works():
    """让模型幻觉，验证禁止词检查能抓出来（这条应为绿）。"""
    out = ask("退款政策是什么？", mode="hallucinate")
    with pytest.raises(AssertionError, match="发现幻觉词"):
        check_no_hallucination(out, FORBIDDEN_HALLUCINATION)


def test_format_checker_works():
    """让模型输出带前缀的"JSON"，验证格式检查能抓出来（这条应为绿）。"""
    raw = ask("提取退款信息", mode="flaky_format")
    with pytest.raises(AssertionError, match="不是纯 JSON"):
        check_is_pure_json(raw)


pytestmark = pytest.mark.llm
