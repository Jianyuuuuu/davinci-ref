#!/usr/bin/env python3
"""
search_knowledge.py — 知识库检索脚本
用法: python3 search_knowledge.py <查询词> [--top N] [--json]

返回与查询最相关的知识块，支持关键词 + BM25 混合排序。
"""
import sys
import json
import math
import re
from pathlib import Path

INDEX_FILE = Path(__file__).parent / "knowledge_index.json"
DEFAULT_TOP = 8

# ── BM25 参数 ────────────────────────────────────────────
BM25_K1 = 1.5
BM25_B = 0.75


def load_index() -> list[dict]:
    return json.loads(INDEX_FILE.read_text(encoding="utf-8"))


def tokenize(text: str) -> list[str]:
    """中英文分词（简单空格 + 逐字）"""
    words = re.findall(r"[\w\u4e00-\u9fff]+", text.lower())
    return words


def bm25_score(query_tokens: list[str], doc_tokens: list[str],
               avgdl: float, doc_len: int,
               idf: dict[str, float]) -> float:
    score = 0.0
    for t in query_tokens:
        if t not in idf:
            continue
        tf = doc_tokens.count(t)
        if tf == 0:
            continue
        idf_val = idf[t]
        numerator = tf * (BM25_K1 + 1)
        denominator = tf + BM25_K1 * (1 - BM25_B + BM25_B * doc_len / avgdl)
        score += idf_val * numerator / denominator
    return score


def compute_idf(docs_tokens: list[list[str]]) -> dict[str, float]:
    N = len(docs_tokens)
    idf = {}
    for tokens in docs_tokens:
        for t in set(tokens):
            idf[t] = idf.get(t, 0) + 1
    for t, df in idf.items():
        idf[t] = math.log((N - df + 0.5) / (df + 0.5) + 1)
    return idf


def search(query: str, top: int = DEFAULT_TOP, json_output: bool = False) -> list[dict]:
    chunks = load_index()
    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    # 预计算
    docs_tokens = [tokenize(c["content"]) for c in chunks]
    avgdl = sum(len(d) for d in docs_tokens) / len(docs_tokens)
    idf = compute_idf(docs_tokens)

    # 关键词命中权重（先匹配 chapter/section 标题）
    title_boost = {}
    for i, chunk in enumerate(chunks):
        title_text = f"{chunk['chapter']} {chunk['section']} {chunk['content'][:200]}"
        title_tokens = set(tokenize(title_text))
        hits = sum(1 for t in query_tokens if t in title_tokens)
        title_boost[i] = hits * 2.0  # 标题命中权重

    # BM25 分数
    scores = []
    for i, doc_tokens in enumerate(docs_tokens):
        bm = bm25_score(query_tokens, doc_tokens, avgdl, len(doc_tokens), idf)
        scores.append(bm + title_boost[i])

    # 取 Top
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top]

    results = []
    for i in top_indices:
        if scores[i] > 0:
            results.append({
                "rank": len(results) + 1,
                "chapter": chunks[i]["chapter"],
                "section": chunks[i]["section"],
                "content": chunks[i]["content"],
                "source": chunks[i]["source"],
                "page": chunks[i].get("page", 0),
                "toc_title": chunks[i].get("toc_title", ""),
                "toc_page": chunks[i].get("toc_page", 0),
                "toc_level": chunks[i].get("toc_level", 0),
                "toc_path": chunks[i].get("toc_path", ""),
                "score": round(scores[i], 3),
            })

    return results


def format_results(results: list[dict], query: str) -> str:
    if not results:
        return f"没有找到与「{query}」相关的内容。"

    out = [f"**检索结果：{len(results)} 条相关知识**\n"]
    for r in results:
        chapter = r["chapter"]
        section = r["section"]
        content = r["content"]
        source = r["source"]

        # 截取与查询最相关的段落（找含查询词的句子）
        content_snippet = content[:600] + ("..." if len(content) > 600 else "")

        out.append(f"---\n**{chapter}**")
        if section:
            out.append(f"> {section}")
        page = r.get("page", 0)
        source_short = r["source"].replace("_structured", "").replace("DaVinci_Resolve_", "DaVinci ")
        toc_path = r.get("toc_path")
        if page:
            out.append(f"> 📄 第 {page} 页 | 来源: {source_short}")
        else:
            out.append(f"> 来源: {source_short}")
        if toc_path:
            out.append(f"> 目录: {toc_path}")
        out.append(content_snippet)
        out.append("")

    return "\n".join(out)


if __name__ == "__main__":
    args = sys.argv[1:]
    json_flag = "--json" in args
    top = DEFAULT_TOP
    if "--top" in args:
        idx = args.index("--top")
        top = int(args[idx + 1])
        args = args[:idx] + args[idx + 2:]

    query = " ".join(args) if args else "cut page"
    results = search(query, top=top)

    if json_flag:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(format_results(results, query))
