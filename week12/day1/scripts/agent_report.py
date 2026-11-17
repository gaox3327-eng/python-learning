"""Agent 评测报告：10 任务 × 5 模式，输出 4 指标。

用法：python scripts/agent_report.py
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ai_evals.agent import FORBIDDEN_TOOLS, run  # noqa: E402

CONFIG = yaml.safe_load((ROOT / "cases" / "agent_cases.yaml").read_text(encoding="utf-8"))
CASES = CONFIG["test_agent"]
GLOBAL_FORBID = set(CONFIG.get("defaults", {}).get("forbid_tools", []))
MODES = ["good", "skip_check", "hallucinate", "wrong_tool", "too_many"]


def norm(s):
    return str(s).replace(" ", "").lower()


def eval_case(case, mode):
    r = run(case["task"], mode=mode)
    tools = [s["tool"] for s in r["steps"]]
    answer_ok = all(norm(w) in norm(r["answer"]) for w in case.get("expect_answer_contains") or [])
    forbid = GLOBAL_FORBID | set(case.get("forbid_tools") or [])
    used = set(tools) & forbid
    steps_ok = ("expect_steps" not in case) or (len(tools) == case["expect_steps"])
    tools_ok = ("expect_tools" not in case) or (tools == case["expect_tools"])
    fin_ok = ("expect_finished" not in case) or (r["finished"] is case["expect_finished"])
    return dict(task_ok=answer_ok and not used, traj_ok=steps_ok and tools_ok and fin_ok and not used,
                steps=len(tools), expect=case.get("expect_steps", len(tools)), used=sorted(used))


def main():
    lines = ["# Agent 行为评测报告", "",
             f"评测集：cases/agent_cases.yaml（{len(CASES)} 个任务）", "",
             "| 模式 | 任务成功率 | 轨迹合规率 | 步数效率 | 越权率 |", "|---|---|---|---|---|"]
    for m in MODES:
        rows = [eval_case(c, m) for c in CASES]
        n = len(rows)
        actual = sum(r["steps"] for r in rows)
        eff = f"{sum(r['expect'] for r in rows)/actual:.2f}" if actual else "—"
        line = (f"| {m} | {sum(r['task_ok'] for r in rows)/n:.0%} "
                f"| {sum(r['traj_ok'] for r in rows)/n:.0%} "
                f"| {eff} "
                f"| {sum(1 for r in rows if r['used'])/n:.0%} |")
        lines.append(line)
    report = "\n".join(lines) + "\n"
    out = ROOT / "reports" / "agent_report.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"已写入 {out}")


if __name__ == "__main__":
    main()
