"""LLM 输出评测报告：20 条评测集，输出 4 指标。

用法：python scripts/llm_report.py [--temp 0.9] [--repeat 5]
"""
import argparse
import collections
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ai_evals.llm import ask  # noqa: E402

FORMAT_ERRORS = ["Traceback", "Exception", "null", "undefined", "None"]


def norm(s):
    if s is None:
        return ""
    s = str(s).replace("～", "-").replace("~", "-").replace("－", "-").replace("\u3000", " ")
    return re.sub(r"\s+", "", s).lower()


def check(case, answer):
    miss = [k for k in case.get("expect_contains", []) if norm(k) not in norm(answer)]
    bad = [k for k in case.get("expect_not_contains", []) if norm(k) in norm(answer)]
    fmt = [w for w in FORMAT_ERRORS if norm(w) in norm(answer)]
    over = case.get("expect_max_len") is not None and len(answer) > case["expect_max_len"]
    return dict(ok=not (miss or bad or fmt or over), bad=bad, fmt=fmt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--temp", type=float, default=0.0)
    ap.add_argument("--repeat", type=int, default=5)
    args = ap.parse_args()

    cases = yaml.safe_load((ROOT / "cases" / "llm_cases.yaml").read_text(encoding="utf-8"))["llm_eval"]
    rows = []
    for c in cases:
        ans = ask(c["question"], temperature=args.temp)
        r = check(c, ans)
        r["category"] = c["category"]
        rows.append(r)

    n = len(rows)
    pass_rate = sum(r["ok"] for r in rows) / n
    fmt_rate = sum(1 for r in rows if not r["fmt"]) / n
    bad_rate = sum(1 for r in rows if r["bad"]) / n

    if args.temp <= 0 or args.repeat <= 1:
        cons = 1.0
    else:
        ratios = []
        for c in cases:
            seen = collections.Counter(
                norm(ask(c["question"], temperature=args.temp, seed=i)) for i in range(args.repeat))
            ratios.append(seen.most_common(1)[0][1] / args.repeat)
        cons = sum(ratios) / len(ratios)

    lines = ["# LLM 输出评测报告", "",
             f"评测集：cases/llm_cases.yaml（{n} 条）　温度：{args.temp}", "",
             "| 指标 | 数值 |", "|---|---|",
             f"| 通过率 | {pass_rate:.1%} |",
             f"| 一致性 | {cons:.1%} |",
             f"| 格式合规率 | {fmt_rate:.1%} |",
             f"| 违规率 | {bad_rate:.1%} |", "",
             "| 分类 | 通过率 |", "|---|---|"]
    by = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        by[r["category"]][1] += 1
        by[r["category"]][0] += int(r["ok"])
    for cat, (ok, tot) in sorted(by.items()):
        lines.append(f"| {cat} | {ok}/{tot} |")

    report = "\n".join(lines) + "\n"
    out = ROOT / "reports" / "llm_report.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"已写入 {out}")


if __name__ == "__main__":
    main()
