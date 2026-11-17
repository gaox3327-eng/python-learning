"""第 17 课：RAG 评测引擎（本地、零依赖、零成本）

RAG 的两段式结构：
    检索 retrieve(query) -> [doc_id, ...]
    生成 answer(query)   -> {"answer": str, "citations": [doc_id]}

评测要点（对应业界指标）：
    检索质量   Recall@k / MRR / nDCG@k
    生成质量   引用合规率（引用的文档必须在检索结果里）
               忠实度 faithfulness（答案内容必须被引用文档支持）

缺陷模式（用于变异测试）：
    good                 正常
    wrong_doc            用排名最后的文档作答（检索排序无效）
    no_citation          答案不给出处
    hallucinate_citation 引用一个根本没检索到的文档（编造来源）
"""

import math
import re

# ── 极简知识库（电商客服场景）
CORPUS = {
    "doc_refund_time": "退款通常在1-3个工作日到账，具体以银行处理时间为准。",
    "doc_refund_rule": "退款金额不得超过订单总额，超过部分无法退回。",
    "doc_shipping": "单笔订单满99元免运费，否则收取10元运费。",
    "doc_invoice": "电子发票会在订单完成后24小时内发送到注册邮箱。",
    "doc_stock": "库存会在下单成功后立即扣减，售罄后无法下单。",
    "doc_member": "会员积分按订单金额的1%累计，积分可在下次购物抵扣。",
    "doc_delivery": "默认使用顺丰配送，偏远地区可能延迟1-2天。",
    "doc_return": "商品签收后7天内可申请退货，需保持包装完整。",
}

TITLES = {
    "doc_refund_time": "退款时效", "doc_refund_rule": "退款规则",
    "doc_shipping": "运费政策", "doc_invoice": "发票开具",
    "doc_stock": "库存规则", "doc_member": "会员积分",
    "doc_delivery": "配送说明", "doc_return": "退货政策",
}


# ──────────────────── 检索：字符 bigram + TF-IDF + 余弦
def _tokens(text: str) -> list[str]:
    text = text.lower()
    words = re.findall(r"[a-z0-9]+", text)
    cjk = "".join(re.findall(r"[\u4e00-\u9fff]", text))
    bigrams = [cjk[i:i + 2] for i in range(len(cjk) - 1)]
    return words + bigrams


def _index():
    df, tf = {}, {}
    for did, text in CORPUS.items():
        counts = {}
        for tk in _tokens(text):
            counts[tk] = counts.get(tk, 0) + 1
        tf[did] = counts
        for tk in counts:
            df[tk] = df.get(tk, 0) + 1
    n = len(CORPUS)
    idf = {tk: math.log((n + 1) / (v + 1)) + 1 for tk, v in df.items()}
    vecs = {}
    for did, counts in tf.items():
        vec = {tk: c * idf.get(tk, 1.0) for tk, c in counts.items()}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        vecs[did] = {tk: v / norm for tk, v in vec.items()}
    return vecs, idf


VECS, IDF = _index()


def _query_vec(query: str) -> dict:
    counts = {}
    for tk in _tokens(query):
        counts[tk] = counts.get(tk, 0) + 1
    vec = {tk: c * IDF.get(tk, 1.0) for tk, c in counts.items()}
    norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
    return {tk: v / norm for tk, v in vec.items()}


def retrieve(query: str, k: int = 3) -> list[str]:
    """返回按相关度降序的 doc_id 列表。"""
    qv = _query_vec(query)
    scored = []
    for did, dv in VECS.items():
        score = sum(w * dv.get(tk, 0.0) for tk, w in qv.items())
        scored.append((score, did))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [did for _, did in scored[:k]]


# ──────────────────── 生成
def answer(query: str, mode: str = "good", k: int = 3) -> dict:
    hits = retrieve(query, k=k)
    if not hits:
        return {"query": query, "answer": "没有找到相关资料。", "citations": [], "retrieved": []}

    if mode == "wrong_doc":
        doc_id = hits[-1]                       # 故意用最不相关的
    else:
        doc_id = hits[0]

    body = CORPUS[doc_id]
    if mode == "no_citation":
        return {"query": query, "answer": f"根据平台规则：{body}", "citations": [], "retrieved": hits}
    if mode == "hallucinate_citation":
        return {"query": query, "answer": f"根据平台规则：{body}",
                "citations": ["doc_9999"], "retrieved": hits}
    return {"query": query, "answer": f"根据《{TITLES[doc_id]}》：{body}",
            "citations": [doc_id], "retrieved": hits}


# ──────────────────── 指标
def recall_at_k(retrieved, gold, k=3):
    return 1.0 if gold in retrieved[:k] else 0.0


def mrr(retrieved, gold):
    for i, did in enumerate(retrieved, 1):
        if did == gold:
            return 1.0 / i
    return 0.0


def ndcg_at_k(retrieved, gold, k=3):
    dcg = 0.0
    for i, did in enumerate(retrieved[:k], 1):
        if did == gold:
            dcg += 1.0 / math.log2(i + 1)
    idcg = 1.0 / math.log2(2)                   # 理想情况：gold 排第 1
    return dcg / idcg


def citation_compliance(citations, retrieved):
    """引用的每条都必须来自检索结果（不能编造来源）。"""
    if not citations:
        return 0.0
    return 1.0 if set(citations) <= set(retrieved) else 0.0


def faithfulness(ans, gold_doc_id, threshold=0.6):
    """忠实度：答案正文与 gold 文档的字面重合度（简化的 claim 支持判定）。"""
    body = ans.split("：", 1)[-1]
    gold = CORPUS.get(gold_doc_id, "")
    gold_chars = set(gold)
    if not body or not gold_chars:
        return 0.0
    overlap = len(set(body) & gold_chars) / len(set(body))
    return 1.0 if overlap >= threshold else overlap
