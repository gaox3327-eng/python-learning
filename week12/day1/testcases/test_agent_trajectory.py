"""第 15 课：数据驱动地跑 agent.yaml 里的 10 个任务

断言全部来自数据（expect_steps / expect_tools / expect_args /
forbid_tools / expect_finished / expect_answer_contains），
代码里不写死任何任务细节——新增任务只改 yaml。
"""

import sys
from pathlib import Path

import pytest
import yaml

from ai_evals.agent import run  # noqa: E402

CASES_FILE = Path(__file__).resolve().parent.parent / "cases" / "agent_cases.yaml"
CONFIG = yaml.safe_load(CASES_FILE.read_text(encoding="utf-8"))
CASES = CONFIG["test_agent"]
GLOBAL_FORBID = set(CONFIG.get("defaults", {}).get("forbid_tools", []))


def norm(s: str) -> str:
    return str(s).replace(" ", "").lower()


def tools_of(result) -> list[str]:
    return [s["tool"] for s in result["steps"]]


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_agent_task(case):
    result = run(case["task"], mode="good")
    tools = tools_of(result)

    # ① 步数
    if "expect_steps" in case:
        assert len(tools) == case["expect_steps"], (
            f"步数期望 {case['expect_steps']}，实际 {len(tools)}：{tools}")

    # ② 工具序列（顺序也校验）
    if "expect_tools" in case:
        assert tools == case["expect_tools"], f"工具序列期望 {case['expect_tools']}，实际 {tools}"

    # ③ 参数（只校验数据里写明的键）
    for expected in case.get("expect_args") or []:
        tool, want = expected["tool"], expected["args"]
        matched = [s for s in result["steps"] if s["tool"] == tool]
        assert matched, f"没有调用 {tool}"
        got = matched[0]["args"]
        for k, v in want.items():
            assert got.get(k) == v, f"{tool} 参数 {k} 期望 {v!r}，实际 {got.get(k)!r}"

    # ④ 黑名单（全局 + 本条）
    forbidden = GLOBAL_FORBID | set(case.get("forbid_tools") or [])
    used_forbidden = set(tools) & forbidden
    assert not used_forbidden, f"调用了禁用工具：{sorted(used_forbidden)}"

    # ⑤ 是否在步数预算内结束
    if "expect_finished" in case:
        assert result["finished"] is case["expect_finished"]

    # ⑥ 答案关键事实
    answer = norm(result["answer"])
    for word in case.get("expect_answer_contains") or []:
        assert norm(word) in answer, f"答案缺少 {word!r}，实际：{result['answer'][:60]}"


pytestmark = pytest.mark.agent
