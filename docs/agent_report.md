# Agent 行为评测报告

评测集：cases/agent_cases.yaml（10 个任务）

| 模式 | 任务成功率 | 轨迹合规率 | 步数效率 | 越权率 |
|---|---|---|---|---|
| good | 100% | 100% | 1.00 | 0% |
| skip_check | 80% | 80% | 1.29 | 0% |
| hallucinate | 10% | 30% | — | 0% |
| wrong_tool | 0% | 0% | 0.45 | 100% |
| too_many | 90% | 0% | 0.15 | 10% |

---

覆盖率：`ai_evals/agent.py` 81%（合计 76%）

复现：`pytest --cov=ai_evals --cov-report=term`
