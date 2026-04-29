# davinci-ref

> DaVinci Resolve 官方手册知识库 — 支持检索、章节出处、PDF 页码、PDF 内置目录路径。轻量版，不内置 PDF。

## 功能

- **自然语言问答**：用中文或英文提问，搜索官方手册原文
- **出处可溯**：每条结果包含章节、标题、页码、PDF 内置目录路径
- **轻量离线索引**：约 22MB，不包含 424MB PDF 原件
- **离线测试**：提供 unittest，验证索引、页码、目录绑定

## 知识库规模

| 文档 | 页数 | 说明 |
|------|------|------|
| DaVinci Resolve 20.3 Reference Manual | 4300 | 参考手册主本 |
| DaVinci Resolve 20 Reference Manual | 4234 | 参考手册 |
| DaVinci Resolve 21 New Features Guide | 150 | 新功能指南 |
| DaVinci Resolve 20 Colorist Guide | 496 | 调色指南 |
| DaVinci Resolve 20 Fusion Visual Effects | 223 | Fusion 视觉特效指南 |
| DaVinci Resolve 20 Advanced Visual Effects | 229 | 高级视觉特效指南 |

**总计：9,632 个知识块，206 个章节。**

## 使用方法

### 检索

```bash
python3 search_knowledge.py "speed ramp" --top 5
python3 search_knowledge.py "retime controls" --top 5
python3 search_knowledge.py "HDR setup" --top 3
```

### JSON 输出

```bash
python3 search_knowledge.py "speed ramp" --top 3 --json
```

每条结果包含：

- `chapter`
- `section`
- `page`
- `toc_title`
- `toc_page`
- `toc_path`
- `source`
- `content`

## 回答规范

接入 Agent 时，每次回答 DaVinci Resolve 问题都必须带出处：

```text
来源：DaVinci Resolve 20.3 Reference Manual
章节：Chapter 51: Speed Effects
标题：To add a speed ramp
页码：第 1098 页
目录：Editing Effects and Transitions > Speed Effects > Clip Retiming Controls > Creating Variable Speed Effects Using the Retime Controls
```

## PDF 定位

本仓库不保存 PDF 原件，但保留 `source + page + toc_path`，可定位到官方 PDF 的对应页面。

## 测试

```bash
python3 -m unittest tests.test_davinci_ref -v
```

当前测试覆盖：

- `knowledge_index.json` 存在
- `toc_index.json` 存在
- 包含 6 个 source
- 绝大多数 chunk 有 `page > 0`
- 绝大多数 chunk 绑定 `toc_title / toc_path`
- Speed Ramp 定位到 20.3 手册第 1098 页
- TOC 路径包含 Speed Effects / Clip Retiming Controls / Creating Variable Speed Effects Using the Retime Controls

## 文件说明

| 文件/目录 | 说明 |
|------|------|
| `SKILL.md` | OpenClaw Skill 说明与回答规范 |
| `knowledge_index.json` | 可检索知识索引 |
| `toc_index.json` | PDF 内置目录索引 |
| `process_davinci.py` | PDF → Markdown（重建时使用） |
| `extract_toc.py` | 提取 PDF 内置目录（重建时使用） |
| `index_knowledge.py` | 构建知识索引并绑定 TOC |
| `search_knowledge.py` | 检索脚本 |
| `tests/test_davinci_ref.py` | 单元测试 |

## 版权

知识库内容来自 Blackmagic Design 官方发布的 DaVinci Resolve 文档，版权归原作者所有。本项目仅做结构化处理与本地检索。