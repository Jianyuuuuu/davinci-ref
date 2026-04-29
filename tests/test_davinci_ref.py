#!/usr/bin/env python3
"""
tests/test_davinci_ref.py — DaVinci Resolve 知识库离线单元测试

测试知识库索引、页码、PDF 内置目录绑定是否正常。
不依赖 PDF 原文件、不跑截图、不跑 OCR。

运行方法:
    cd /Users/jianyu/.agent/skills/team_skills/davinci-ref
    python3 -m unittest tests.test_davinci_ref -v
"""
import json
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
INDEX_FILE = SKILL_DIR / "knowledge_index.json"
TOC_FILE = SKILL_DIR / "toc_index.json"

SRC_20_3 = "DaVinci_Resolve_20.3_Reference_Manual_structured"
PAGE_SPEED_RAMP = 1098
SPEED_RAMP_KEYWORDS = [
    "Speed Effects",
    "Clip Retiming Controls",
    "Creating Variable Speed Effects Using the Retime Controls",
]


class TestKnowledgeIndex(unittest.TestCase):
    """验证 knowledge_index.json 的结构和内容。"""

    @classmethod
    def setUpClass(cls):
        cls.index_file = INDEX_FILE
        with open(INDEX_FILE, encoding="utf-8") as f:
            cls.chunks = json.load(f)

    def test_index_file_exists(self):
        self.assertTrue(self.index_file.exists(), f"索引文件不存在: {self.index_file}")

    def test_toc_file_exists(self):
        self.assertTrue(TOC_FILE.exists(), f"目录索引不存在: {TOC_FILE}")

    def test_index_has_six_sources(self):
        sources = {c["source"] for c in self.chunks}
        expected = {
            "DaVinci_Resolve_20.3_Reference_Manual_structured",
            "DaVinci_Resolve_20_Reference_Manual_structured",
            "DaVinci_Resolve_21_New_Features_Guide_structured",
            "DaVinci_Resolve_20_Colorist_Guide_structured",
            "DaVinci_Resolve_20_Fusion_Visual_Effects_structured",
            "DaVinci_Resolve_20_Advanced_Visual_Effects_structured",
        }
        self.assertEqual(sources, expected, "Source 列表与预期不符")

    def test_chunks_have_page_field(self):
        total = len(self.chunks)
        with_page = sum(1 for c in self.chunks if isinstance(c.get("page"), int) and c["page"] > 0)
        ratio = with_page / total
        self.assertGreaterEqual(ratio, 0.99, f"page>0 比例仅 {ratio:.2%} ({with_page}/{total})")

    def test_chunks_have_toc_binding(self):
        total = len(self.chunks)
        with_toc = sum(1 for c in self.chunks if c.get("toc_title") and c.get("toc_path"))
        ratio = with_toc / total
        self.assertGreaterEqual(ratio, 0.99, f"TOC 绑定比例仅 {ratio:.2%} ({with_toc}/{total})")

    def test_speed_ramp_chunk_1098(self):
        matches = [
            c for c in self.chunks
            if c.get("source") == SRC_20_3 and c.get("page") == PAGE_SPEED_RAMP
        ]
        self.assertTrue(matches, f"在 {SRC_20_3} 第 {PAGE_SPEED_RAMP} 页未找到 chunk")

        good_toc = [
            c for c in matches
            if all(kw in c.get("toc_path", "") for kw in SPEED_RAMP_KEYWORDS)
        ]
        self.assertGreater(len(good_toc), 0, "未找到带正确 TOC 路径的 speed ramp chunk")

        speed_ramp_chunks = [
            c for c in matches
            if "speed ramp" in c.get("content", "").lower()
            or "speed ramp" in c.get("section", "").lower()
        ]
        self.assertGreater(len(speed_ramp_chunks), 0, "第 1098 页没有包含 speed ramp 的 chunk")


if __name__ == "__main__":
    unittest.main(verbosity=2)
