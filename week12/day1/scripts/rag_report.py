"""第 17 课：RAG 评测报告

用法：python scripts/rag_report.py
输出：reports/rag_report.md
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ai_evals import rag  # noqa: E402

CASES = yaml.safe_load((ROOT / "cases" / "rag_cases.yaml").read_text(encoding="utf-8"))["rag_cases"]
K = 3


def main():
    lines = ["# RAG 评测报告", "", f"评测集：cases/rag_cases.yaml（{len(CASES)} 条查询，知识库 8 篇）", ""]

    # ── 检索指标
    recalls, mrrs, ndcgs = [], [], []
    detail = ["| 查询 | 标准文档 | top1 | Recall@3 | MRR | nDCG@3 |", "|---|---|---|---|---|---|"]
    for c in CASES:
        hits = rag.retrieve(c["query"], k=K)
        r = rag.recall_at_k(hits, c["gold_doc"], K)
        m = rag.mrr(hits, c["gold_doc"])
        n = rag.ndcg_at_k(hits, c["gold_doc"], K)
        recalls.append(r); mrrs.append(m); ndcgs.append(n)
        detail.append(f"| {c['id']} | {c['gold_doc']} | {hits[0]} | {r:.0f} | {m:.2f} | {n:.2f} |")

    n = len(CASES)
    lines += ["## 一、检索指标", "",
              "| 指标 | 数值 | 说明 |", "|---|---|---|",
              f"| Recall@3 | {sum(recalls)/n:.1%} | 标准文档是否出现在前 3 条 |",
              f"| MRR | {sum(mrrs)/n:.3f} | 第一个正确文档排名的倒数均值（1.0 = 永远第 1） |",
              f"| nDCG@3 | {sum(ndcgs)/n:.3f} | 排序质量（考虑位置折损） |", ""]

    # ── 生成指标（good 模式）
    cite, faith, fact = [], [], []
    for c in CASES:
        r = rag.answer(c["query"], mode="good")
        cite.append(rag.citation_compliance(r["citations"], r["retrieved"]))
        faith.append(rag.faithfulness(r["answer"], c["gold_doc"]))
        fact.append(all(w in r["answer"] for w in c["expect_contains"]))
    lines += ["## 二、生成指标（正常模式）", "",
              "| 指标 | 数值 | 说明 |", "|---|---|---|",
              f"| 引用合规率 | {sum(cite)/n:.1%} | 引用的文档必须来自检索结果 |",
              f"| 忠实度 | {sum(faith)/n:.1%} | 答案内容被引用文档支持的比例 |",
              f"| 事实命中率 | {sum(fact)/n:.1%} | 答案含全部事实锚点 |", ""]

    # ── 缺陷模式对比
    lines += ["## 三、缺陷模式对比（变异测试）", "",
              "| 模式 | 引用合规率 | 忠实度 | 说明 |", "|---|---|---|---|"]
    for mode, desc in [("good", "正常"), ("wrong_doc", "用排名最后的文档作答"),
                       ("no_citation", "答案无出处"), ("hallucinate_citation", "编造引用")]:
        cs, fs = [], []
        for c in CASES:
            r = rag.answer(c["query"], mode=mode)
            cs.append(rag.citation_compliance(r["citations"], r["retrieved"]))
            fs.append(rag.faithfulness(r["answer"], c["gold_doc"]))
        lines.append(f"| {mode} | {sum(cs)/n:.0%} | {sum(fs)/n:.0%} | {desc} |")
    lines.append("")

    lines += ["## 四、逐条明细", ""] + detail + [""]

    report = "\n".join(lines)
    out = ROOT / "reports" / "rag_report.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"已写入 {out}")


if __name__ == "__main__":
    main()
