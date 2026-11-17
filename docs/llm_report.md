# LLM 输出评测报告

评测集：cases/llm_cases.yaml（20 条）　温度：0.0

| 指标 | 数值 |
|---|---|
| 通过率 | 95.0% |
| 一致性 | 100.0% |
| 格式合规率 | 100.0% |
| 违规率 | 0.0% |

| 分类 | 通过率 |
|---|---|
| adversarial | 5/5 |
| boundary | 5/5 |
| normal | 4/5 |
| refusal | 5/5 |

---

覆盖率：`ai_evals/llm.py` 69%（合计 76%）

复现：`pytest --cov=ai_evals --cov-report=term`
