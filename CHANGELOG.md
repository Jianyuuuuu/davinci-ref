# Changelog

## 2026-04-29

### Changed

- 扩展知识库来源到 6 本 DaVinci Resolve 官方文档。
- 索引规模更新为 9,632 个知识块，206 个章节。
- `search_knowledge.py` 输出新增出处字段：
  - `page`
  - `toc_title`
  - `toc_page`
  - `toc_level`
  - `toc_path`
- `index_knowledge.py` 新增 PDF 内置目录绑定逻辑，根据 `source + page` 为 chunk 绑定最近的 TOC 路径。
- 修复 page 注释解析顺序，避免上一段正文被错误标记为下一页。
- 改为轻量版：移除内置 PDF 文件与截图能力，skill 体积从约 446MB 降到约 22MB。

### Added

- 新增 `extract_toc.py`：从 PDF 内置目录生成 `toc_index.json`。
- 新增 `process_davinci.py` / `clean_md.py` / `extract_md.py`：用于重建结构化 Markdown。
- 新增 `toc_index.json`：保存 6 本 PDF 的内置目录结构。
- 新增 `tests/test_davinci_ref.py`：离线单元测试，不依赖 PDF 原文件。

### Verified

- `python3 -m unittest tests.test_davinci_ref -v`：6/6 通过。
- `speed ramp` 定位结果：
  - 来源：DaVinci Resolve 20.3 Reference Manual
  - 章节：Chapter 51: Speed Effects
  - 页码：第 1098 页
  - 目录：Editing Effects and Transitions > Speed Effects > Clip Retiming Controls > Creating Variable Speed Effects Using the Retime Controls
