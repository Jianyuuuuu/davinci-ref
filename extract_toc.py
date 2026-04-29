#!/usr/bin/env python3
"""
extract_toc.py — 导出 DaVinci Resolve PDF 内置目录为 toc_index.json
"""
import json
from pathlib import Path
import fitz

PDF_DIR = Path(__file__).parent / "pdfs"

PDF_MAP = {
    "DaVinci_Resolve_20.3_Reference_Manual_structured": PDF_DIR / "DaVinci_Resolve_20.3_Reference_Manual.pdf",
    "DaVinci_Resolve_20_Reference_Manual_structured": PDF_DIR / "DaVinci_Resolve_20_Reference_Manual.pdf",
    "DaVinci_Resolve_21_New_Features_Guide_structured": PDF_DIR / "DaVinci_Resolve_21_New_Features_Guide.pdf",
    "DaVinci_Resolve_20_Colorist_Guide_structured": PDF_DIR / "DaVinci_Resolve_20_Colorist_Guide.pdf",
    "DaVinci_Resolve_20_Fusion_Visual_Effects_structured": PDF_DIR / "DaVinci_Resolve_20_Fusion_Visual_Effects.pdf",
    "DaVinci_Resolve_20_Advanced_Visual_Effects_structured": PDF_DIR / "DaVinci_Resolve_20_Advanced_Visual_Effects.pdf",
}

OUT = Path(__file__).parent / "toc_index.json"

def build_toc():
    index = {}
    for source, pdf in PDF_MAP.items():
        path = Path(pdf)
        if not path.exists():
            print(f"跳过，PDF 不存在: {path}")
            continue
        doc = fitz.open(str(path))
        toc = doc.get_toc(simple=True)  # [level, title, page]
        rows = []
        stack = []
        for level, title, page in toc:
            # 维护层级路径
            stack = stack[: max(level - 1, 0)]
            stack.append(title)
            rows.append({
                "level": level,
                "title": title,
                "page": page,
                "path": " > ".join(stack),
            })
        index[source] = {
            "pdf": str(path),
            "pages": len(doc),
            "toc_count": len(rows),
            "toc": rows,
        }
        doc.close()
        print(f"{source}: {len(rows)} 条目录")
    OUT.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"完成: {OUT}")

if __name__ == "__main__":
    build_toc()
