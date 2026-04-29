#!/usr/bin/env python3
"""
DaVinci Resolve 官方手册 → 结构化 Markdown
用法:
    python3 process_davinci.py <pdf_path> [output_dir]
"""

import sys
import re
import json
from pathlib import Path
from pypdf import PdfReader

# ─────────────────────────────────────────
# 1. 清理：将 PDF 转成干净的单页 Markdown
# ─────────────────────────────────────────
def pdf_to_clean_markdown(pdf_path: str, output_dir: str = ".") -> str:
    """把 PDF 每一页转成一组 `## Page N\n...` 条目，存入一个 .md 文件"""
    pdf_path = Path(pdf_path)
    out_path = Path(output_dir) / f"{pdf_path.stem}_clean.md"

    reader = PdfReader(pdf_path)
    total = len(reader.pages)

    lines = []
    for i, page in enumerate(reader.pages):
        i1 = i + 1  # 1-indexed page number
        text = page.extract_text() or ""
        text = text.strip()
        if not text:
            text = "(此页无文字内容)"
        lines.append(f"## Page {i1}\n{text}")

    out_path.write_text("\n\n".join(lines), encoding="utf-8")
    print(f"  清理完成: {out_path}  ({total} 页)")
    return str(out_path)


# ─────────────────────────────────────────
# 2. 结构化：从清理好的 Markdown 构建层级
# ─────────────────────────────────────────
def detect_document_type(pages: dict) -> str:
    """根据前20页内容判断是参考手册还是新功能指南"""
    sample = " ".join(str(pages.get(i, ""))[:200] for i in range(1, 21))
    if "Chapter " in sample or "chapter" in sample.lower():
        return "reference"
    return "new_features"


def find_chapter_boundaries(pages: dict, doc_type: str) -> list:
    """
    扫描所有页面，找出章节起始页。
    返回 [(page_num, chapter_title), ...]，按 page_num 升序。
    """
    boundaries = []
    prev_title = None

    for p in sorted(pages.keys()):
        text = str(pages.get(p, ""))
        lines = [l.strip() for l in text.strip().split('\n') if l.strip()]

        if doc_type == "reference":
            # 参考手册："Chapter N" 必须在页面最开头（前3行）
            m = re.match(r"^Chapter\s+(\d+)\s*\n\s*(.+?)\s*$", text.strip(), re.MULTILINE)
            if m:
                title = m.group(2).replace("\n", " ").strip()
                # 跳过封面页（第1页）的误匹配
                if p == 1:
                    continue
                boundaries.append((p, f"Chapter {m.group(1)}: {title}"))

        else:
            # 新功能指南：检测主要功能分类（Contents 列表中的大类）
            if lines:
                first = lines[0]
                if len(first) < 3 or len(first) > 50:
                    continue
                if first[0].islower():
                    continue
                skip_starts = ('The ', 'A ', 'An ', 'NOTE', 'TIP', 'Using', 'How', 'What')
                if any(first.startswith(s) for s in skip_starts):
                    continue
                if first != prev_title:
                    boundaries.append((p, first))
                    prev_title = first

    return boundaries


def get_page_title(pages: dict, page_num: int) -> str:
    """
    从页面正文中提取页面标题（第一个显著段落）。
    策略：取第一行或第一个短于60字符的独立段落。
    """
    text = str(pages.get(page_num, ""))
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    # 跳过 "Chapter N" 或纯数字行
    for line in lines[:8]:
        if re.match(r"^Chapter\s+\d+", line):
            continue
        if re.match(r"^Page\s+\d+", line):
            continue
        if len(line) < 3:
            continue
        # 跳过超长行（通常是正文）
        if len(line) > 80:
            continue
        # 跳过含有大量空格的"点阵线"残留
        if re.search(r"\.{5,}", line):
            continue
        return line
    return ""


def build_structured_markdown(pages: dict, doc_type: str,
                               chapter_boundaries: list,
                               title: str = "") -> str:
    """
    将页数字典构建成「H2 章节 > H3 页面 > 正文」的层级结构。
    """
    sections = []

    # 当前章节（初始为默认值，真实章节出现后会被替换）
    current_chapter = "前言 / Front Matter" if doc_type == "reference" else "简介 / Introduction"

    # 按页码遍历（跳过第1页封面）
    for page_num in sorted(pages.keys()):
        if page_num == 1:
            continue  # 封面页不加入正文

        # 检查是否进入新章节
        for boundary_page, boundary_title in chapter_boundaries:
            if page_num == boundary_page:
                current_chapter = boundary_title
                break

        body = str(pages[page_num]).strip()

        # 清理：去掉头部 "## Page N"
        lines = body.split("\n")
        clean_lines = []
        for line in lines:
            if re.match(r"^## Page \d+$", line.strip()):
                continue
            clean_lines.append(line)
        body = "\n".join(clean_lines).strip()

        # 页面标题
        page_title = get_page_title(pages, page_num)

        sections.append({
            "chapter": current_chapter,
            "page": page_num,
            "title": page_title,
            "body": body,
            "source_page": page_num,
        })

    # 写出
    out_lines = [f"# {title}\n\n---\n"]
    prev_chapter = None
    for sec in sections:
        if sec["chapter"] != prev_chapter:
            out_lines.append(f"\n## {sec['chapter']}\n")
            prev_chapter = sec["chapter"]

        heading = sec["title"] if sec["title"] else f"第{sec['page']}页"
        out_lines.append(f"\n<!-- page: {sec['page']} -->\n### {heading}\n")
        if sec["body"]:
            out_lines.append(sec["body"] + "\n")

    return "".join(out_lines)


def parse_clean_markdown(clean_md_path: str) -> dict:
    """将清理好的 Markdown 解析成 {page_num: body_text} 字典"""
    text = Path(clean_md_path).read_text(encoding="utf-8")
    # 兼容 "## Page N" 和 "# Page N" 两种格式
    parts = re.split(r"(?=##? Page \d+\n)", text)
    pages = {}
    for part in parts:
        if not part.strip():
            continue
        m = re.match(r"##? Page (\d+)\n", part)
        if m:
            page_num = int(m.group(1))
            body = part[len(m.group(0)):]
            pages[page_num] = body
    return pages


# ─────────────────────────────────────────
# 3. 主流程
# ─────────────────────────────────────────
def process_pdf(pdf_path: str, output_dir: str = ".") -> str:
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fname_stem = pdf_path.stem
    clean_md = output_dir / f"{fname_stem}_clean.md"
    structured_md = output_dir / f"{fname_stem}_structured.md"

    # Step 1: PDF → 干净的单页 Markdown
    if not clean_md.exists():
        print(f"[1/3] 清理 PDF: {pdf_path.name}")
        pdf_to_clean_markdown(str(pdf_path), str(output_dir))
    else:
        print(f"[1/3] 复用已有清理文件: {clean_md}")

    # Step 2: 解析页码结构
    print(f"[2/3] 分析章节结构...")
    pages = parse_clean_markdown(str(clean_md))
    print(f"      共 {len(pages)} 页")

    doc_type = detect_document_type(pages)
    print(f"      文档类型: {'参考手册' if doc_type == 'reference' else '新功能指南'}")

    # Step 3: 找章节边界
    chapter_boundaries = find_chapter_boundaries(pages, doc_type)
    print(f"      发现 {len(chapter_boundaries)} 个章节")
    for cb in chapter_boundaries[:10]:
        print(f"        Page {cb[0]}: {cb[1][:60]}")

    # Step 4: 构建并输出结构化 Markdown
    print(f"[3/3] 生成结构化文档...")
    title_map = {
        "reference": f"DaVinci Resolve 参考手册",
        "new_features": f"DaVinci Resolve 新功能指南",
    }
    structured = build_structured_markdown(
        pages, doc_type, chapter_boundaries,
        title=title_map.get(doc_type, pdf_path.stem)
    )
    structured_md.write_text(structured, encoding="utf-8")

    size_kb = len(structured) / 1024
    print(f"  完成: {structured_md}  ({size_kb:.0f} KB)")
    return str(structured_md)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 process_davinci.py <pdf_path> [output_dir]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    if not Path(pdf_path).exists():
        print(f"错误: 文件不存在: {pdf_path}")
        sys.exit(1)

    result = process_pdf(pdf_path, output_dir)
    print(f"\n输出: {result}")


if __name__ == "__main__":
    main()
