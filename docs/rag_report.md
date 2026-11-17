# RAG 评测报告

评测集：cases/rag_cases.yaml（10 条查询，知识库 8 篇）

## 一、检索指标

| 指标 | 数值 | 说明 |
|---|---|---|
| Recall@3 | 100.0% | 标准文档是否出现在前 3 条 |
| MRR | 1.000 | 第一个正确文档排名的倒数均值（1.0 = 永远第 1） |
| nDCG@3 | 1.000 | 排序质量（考虑位置折损） |

## 二、生成指标（正常模式）

| 指标 | 数值 | 说明 |
|---|---|---|
| 引用合规率 | 100.0% | 引用的文档必须来自检索结果 |
| 忠实度 | 100.0% | 答案内容被引用文档支持的比例 |
| 事实命中率 | 100.0% | 答案含全部事实锚点 |

## 三、缺陷模式对比（变异测试）

| 模式 | 引用合规率 | 忠实度 | 说明 |
|---|---|---|---|
| good | 100% | 100% | 正常 |
| wrong_doc | 100% | 20% | 用排名最后的文档作答 |
| no_citation | 0% | 100% | 答案无出处 |
| hallucinate_citation | 0% | 100% | 编造引用 |

## 四、逐条明细

| 查询 | 标准文档 | top1 | Recall@3 | MRR | nDCG@3 |
|---|---|---|---|---|---|
| R01_refund_time | doc_refund_time | doc_refund_time | 1 | 1.00 | 1.00 |
| R02_refund_over | doc_refund_rule | doc_refund_rule | 1 | 1.00 | 1.00 |
| R03_shipping | doc_shipping | doc_shipping | 1 | 1.00 | 1.00 |
| R04_invoice | doc_invoice | doc_invoice | 1 | 1.00 | 1.00 |
| R05_stock | doc_stock | doc_stock | 1 | 1.00 | 1.00 |
| R06_member | doc_member | doc_member | 1 | 1.00 | 1.00 |
| R07_delivery | doc_delivery | doc_delivery | 1 | 1.00 | 1.00 |
| R08_return | doc_return | doc_return | 1 | 1.00 | 1.00 |
| R09_refund_time2 | doc_refund_time | doc_refund_time | 1 | 1.00 | 1.00 |
| R10_shipping_min | doc_shipping | doc_shipping | 1 | 1.00 | 1.00 |
