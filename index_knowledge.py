#!/usr/bin/env python3
"""
build_index.py — 将 DaVinci Resolve 结构化 Markdown 切成知识块，构建可搜索索引
用法: python3 build_index.py
"""
import re
import json
import hashlib
from pathlib import Path

SRC_DIR = Path("/Users/jianyu/Downloads/DaVinci_Manuals/output")
INDEX_FILE = Path(__file__).parent / "knowledge_index.json"
TOC_FILE = Path(__file__).parent / "toc_index.json"

# ── 分块策略 ──────────────────────────────────────────────
# 每章（Chapter）为一个区块；如果一章超过 200 行，切成子块
MAX_LINES = 200

def split_into_chunks(markdown_text: str, chunk_size: int = MAX_LINES) -> list[str]:
    """按行数上限切分子块，保留段落完整性"""
    lines = markdown_text.split("\n")
    chunks = []
    start = 0
    while start < len(lines):
        chunk_lines = lines[start:start + chunk_size]
        # 找到合适的断点（空行处）
        if start + chunk_size < len(lines):
            # 向前找最近的两个空行
            break_idx = len(chunk_lines)
            for i in range(len(chunk_lines) - 1, max(0, len(chunk_lines) // 2), -1):
                if not chunk_lines[i].strip():
                    break_idx = i
                    break
            chunks.append("\n".join(chunk_lines[:break_idx]))
            start += break_idx if break_idx > 0 else chunk_size
        else:
            chunks.append("\n".join(chunk_lines))
            break
    return chunks


def extract_metadata(line: str) -> dict:
    """从 H2 或 H3 行提取元数据"""
    h2 = re.match(r"^## (.+)", line)
    h3 = re.match(r"^### (.+)", line)
    if h2:
        return {"type": "chapter", "title": h2.group(1).strip()}
    if h3:
        return {"type": "section", "title": h3.group(1).strip()}
    return {}


def load_toc_index() -> dict:
    """读取 PDF 内置目录索引。"""
    if not TOC_FILE.exists():
        return {}
    return json.loads(TOC_FILE.read_text(encoding="utf-8"))


def _tok(text: str) -> set[str]:
    return {t for t in re.findall(r"[\w']+", text.lower()) if len(t) > 2}


def bind_toc(chunk: dict, toc_index: dict) -> dict:
    """根据 source + page 绑定最接近的 PDF TOC 条目。

    同一 PDF 页可能有多个目录项；优先在同页目录项中选择与 section/content
    词汇重叠最高的项，否则退回到当前页之前最近的目录项。
    """
    source = chunk.get("source")
    page = chunk.get("page", 0)
    toc_rows = toc_index.get(source, {}).get("toc", [])
    if not toc_rows or not page:
        return chunk

    query_text = f"{chunk.get('section','')} {chunk.get('content','')[:500]}"
    query_tokens = _tok(query_text)

    # 同页目录项优先，用标题/路径词汇重叠选择。
    same_page = [r for r in toc_rows if r["page"] == page]
    if same_page and query_tokens:
        def score(row):
            title_tokens = _tok(f"{row.get('title','')} {row.get('path','')}")
            overlap = len(query_tokens & title_tokens)
            # 轻微偏好更深层目录，通常更接近段落标题
            return (overlap, row.get("level", 0))
        best = max(same_page, key=score)
        if score(best)[0] == 0:
            best = same_page[-1]
    else:
        # 选择 page <= chunk.page 的最后一个目录项
        best = None
        for row in toc_rows:
            if row["page"] <= page:
                best = row
            else:
                break

    if best:
        chunk["toc_title"] = best["title"]
        chunk["toc_page"] = best["page"]
        chunk["toc_level"] = best["level"]
        chunk["toc_path"] = best.get("path", best["title"])
    return chunk


def process_structured_md(path: Path) -> list[dict]:
    """将结构化 Markdown 解析成知识块列表"""
    text = path.read_text(encoding="utf-8")
    blocks = []
    current_chapter = "Unknown Chapter"
    current_section = ""
    current_page = 0
    body_lines = []
    line_count = 0

    def flush():
        nonlocal body_lines, line_count
        if not body_lines:
            return
        body = "\n".join(body_lines).strip()
        if body:
            chunk_id = hashlib.md5(f"{current_chapter}:{current_section}:{body[:50]}".encode()).hexdigest()[:12]
            blocks.append({
                "id": chunk_id,
                "chapter": current_chapter,
                "section": current_section,
                "content": body,
                "source": path.stem,
                "page": current_page,
            })
        body_lines = []
        line_count = 0

    for raw_line in text.split("\n"):
        line = raw_line.rstrip()
        # 解析页码注释（必须在其他标题之前或同时处理）
        page_m = re.match(r"^<!-- page:\s*(\d+)\s*-->$", line)
        if page_m:
            # page 注释标记的是下一段内容；先保存当前段，避免页码错位
            flush()
            current_page = int(page_m.group(1))
            continue
        if re.match(r"^## Chapter", line):
            flush()
            current_chapter = line.lstrip("#").strip()
            current_section = ""
            body_lines = []
            line_count = 0
        elif re.match(r"^### ", line):
            if line_count >= MAX_LINES:
                flush()
            flush()
            current_section = line.lstrip("#").strip()
            body_lines = []
            line_count = 0
        else:
            body_lines.append(line)
            line_count += 1

    flush()
    return blocks


def main():
    chunks = []
    toc_index = load_toc_index()

    for md_file in SRC_DIR.glob("*_structured.md"):
        print(f"处理: {md_file.name}")
        blocks = process_structured_md(md_file)
        blocks = [bind_toc(b, toc_index) for b in blocks]
        chunks.extend(blocks)
        print(f"  → {len(blocks)} 个知识块")

    INDEX_FILE.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\n索引完成: {INDEX_FILE}")
    print(f"总计 {len(chunks)} 个知识块")

    # 输出一些统计信息
    chapters = set(b["chapter"] for b in chunks)
    print(f"涵盖 {len(chapters)} 个章节")
    toc_bound = sum(1 for b in chunks if b.get("toc_title"))
    print(f"绑定目录: {toc_bound}/{len(chunks)}")


if __name__ == "__main__":
    main()
