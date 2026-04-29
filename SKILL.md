---
name: davinci-ref
description: DaVinci Resolve 官方手册知识库 — 支持中英文检索，并输出官方出处的章节、标题、页码、PDF 内置目录路径
trigger: 当用户询问 DaVinci Resolve（达芬奇）的任何功能、设置、操作方法时触发
---

# DaVinci Resolve 参考手册技能

## 用途

当 Arden 询问 DaVinci Resolve 的任何功能、操作方法、设置参数时，快速检索官方手册内容，给出准确答案。

**硬性要求：每次回答 DaVinci Resolve 问题时，必须给出出处：章节、标题、页码。**

本 skill 是轻量版：不内置 PDF 原文件，不提供截图能力。它保留 `page` 和 `toc_path`，用于准确定位到官方 PDF 的对应位置。

## 知识库

- **索引量**：9,632 个知识块，206 个章节
- **体积**：约 22MB（不包含 PDF）
- **来源**：
  - DaVinci Resolve 20.3 Reference Manual（4300 页，参考手册主本）
  - DaVinci Resolve 20 Reference Manual（4234 页，参考手册）
  - DaVinci Resolve 21 New Features Guide（150 页）
  - DaVinci Resolve 20 Colorist Guide（496 页，调色指南）
  - DaVinci Resolve 20 Fusion Visual Effects（223 页，Fusion 视觉特效指南）
  - DaVinci Resolve 20 Advanced Visual Effects（229 页，高级视觉特效指南）
- **语言**：英文原文（回答时翻译成中文）

## 检索工具

```bash
SKILL_DIR="$HOME/.agent/skills/team_skills/davinci-ref"
python3 "$SKILL_DIR/search_knowledge.py" "<查询词>" [--top N] [--json]
```

每个结果包含：

- `chapter`：章节
- `section`：标题 / 小节标题
- `page`：PDF 页码
- `toc_title` / `toc_page` / `toc_path`：PDF 内置目录路径
- `source`：来源 PDF 对应 source 名称
- `content`：官方手册原文片段

## 回答格式要求

回答要先说结论，再给出处。出处必须至少包含：

```text
来源：DaVinci Resolve 20.3 Reference Manual
章节：Chapter 51: Speed Effects
标题：Clip Retiming Controls / To add a speed ramp
页码：第 1098 页
目录：Editing Effects and Transitions > Speed Effects > Clip Retiming Controls > Creating Variable Speed Effects Using the Retime Controls
```

如果检索结果不完全匹配，必须明确说「手册未明确说明」或「这里是根据相邻章节推断」。

## 定位 PDF 的方式

本 skill 不保存 PDF 文件，但会输出官方 PDF 对应的：

- 文档来源：`source`
- PDF 页码：`page`
- PDF 内置目录路径：`toc_path`

因此需要查看原文时，可以根据文档名 + 页码到官方 PDF 中定位。

## 测试

```bash
python3 -m unittest tests.test_davinci_ref -v
```

当前测试覆盖：

- 6 个 source 完整存在
- chunk 大多带 page 和 toc 绑定
- Speed Ramp 定位到 20.3 Reference Manual 第 1098 页
- TOC 路径包含 Speed Effects / Clip Retiming Controls / Creating Variable Speed Effects Using the Retime Controls

## 维护脚本

| 文件 | 作用 |
|------|------|
| `process_davinci.py` | PDF → clean/structured Markdown（重建时使用） |
| `extract_toc.py` | 从 PDF 内置目录生成 `toc_index.json`（重建时使用） |
| `index_knowledge.py` | 从 structured Markdown 生成 `knowledge_index.json`，并绑定 TOC |
| `search_knowledge.py` | 检索知识库 |
| `tests/test_davinci_ref.py` | 离线单元测试 |

## 限制

- 不内置 PDF 原文件
- 不提供截图能力
- 知识库为英文原文，回答时翻译为中文
- 涉及具体数值参数时，优先引用原文
- 若检索结果与问题不完全匹配，必须说明不确定性
