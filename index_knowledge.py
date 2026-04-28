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


def process_structured_md(path: Path) -> list[dict]:
    """将结构化 Markdown 解析成知识块列表"""
    text = path.read_text(encoding="utf-8")
    blocks = []
    current_chapter = "Unknown Chapter"
    current_section = ""
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
            })
        body_lines = []
        line_count = 0

    for raw_line in text.split("\n"):
        line = raw_line.rstrip()
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

    for md_file in SRC_DIR.glob("*_structured.md"):
        print(f"处理: {md_file.name}")
        blocks = process_structured_md(md_file)
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


if __name__ == "__main__":
    main()
