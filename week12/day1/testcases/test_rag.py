"""第 17 课：RAG 评测（检索指标 + 生成指标）

指标：
    检索  Recall@3 / MRR / nDCG@3
    生成  引用合规率 / 忠实度
"""

from pathlib import Path

import pytest
import yaml

from ai_evals import rag

CASES = yaml.safe_load(
    (Path(__file__).resolve().parent.parent / "cases" / "rag_cases.yaml").read_text(encoding="utf-8")
)["rag_cases"]

pytestmark = pytest.mark.rag
K = 3


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_retrieval_finds_gold_document(case):
    """Recall@3：标准文档必须出现在前 3 条检索结果里。"""
    hits = rag.retrieve(case["query"], k=K)
    assert case["gold_doc"] in hits, f"未召回 {case['gold_doc']}，实际 {hits}"


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_retrieval_ranking_is_sane(case):
    """nDCG@3：标准文档排得越靠前越好（要求 ≥0.5，即至少排到第 2 位）。"""
    hits = rag.retrieve(case["query"], k=K)
    assert rag.ndcg_at_k(hits, case["gold_doc"], K) >= 0.5, f"排序质量差：{hits}"


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_answer_is_grounded_and_cited(case):
    """生成侧：答案含事实锚点 + 引用合规 + 忠实度达标。"""
    r = rag.answer(case["query"])
    for word in case["expect_contains"]:
        assert word in r["answer"], f"答案缺少 {word!r}"
    assert rag.citation_compliance(r["citations"], r["retrieved"]) == 1.0
    assert rag.faithfulness(r["answer"], case["gold_doc"]) >= 0.6


def test_aggregate_retrieval_metrics():
    """整体指标：Recall@3 ≥ 0.8，MRR ≥ 0.7。"""
    recalls = [rag.recall_at_k(rag.retrieve(c["query"], K), c["gold_doc"], K) for c in CASES]
    mrrs = [rag.mrr(rag.retrieve(c["query"], K), c["gold_doc"]) for c in CASES]
    assert sum(recalls) / len(recalls) >= 0.8, f"Recall@3={sum(recalls)/len(recalls):.2f}"
    assert sum(mrrs) / len(mrrs) >= 0.7, f"MRR={sum(mrrs)/len(mrrs):.2f}"


def test_hallucinated_citation_is_detected():
    """变异测试：编造来源必须被引用合规检查抓到。"""
    r = rag.answer(CASES[0]["query"], mode="hallucinate_citation")
    assert rag.citation_compliance(r["citations"], r["retrieved"]) == 0.0


def test_missing_citation_is_detected():
    """变异测试：无出处必须被判为不合规。"""
    r = rag.answer(CASES[0]["query"], mode="no_citation")
    assert rag.citation_compliance(r["citations"], r["retrieved"]) == 0.0


def test_wrong_document_hurts_faithfulness():
    """变异测试：用错文档作答，忠实度应显著下降。"""
    good = rag.answer(CASES[0]["query"], mode="good")
    bad = rag.answer(CASES[0]["query"], mode="wrong_doc")
    good_f = rag.faithfulness(good["answer"], CASES[0]["gold_doc"])
    bad_f = rag.faithfulness(bad["answer"], CASES[0]["gold_doc"])
    assert good_f > bad_f, f"good={good_f:.2f} 应高于 bad={bad_f:.2f}"
