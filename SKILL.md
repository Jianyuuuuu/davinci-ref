---
name: davinci-ref
description: DaVinci Resolve 官方手册知识库 — 可回答达芬奇软件操作、设置、节点等问题，支持中英文检索
trigger: 当用户询问 DaVinci Resolve（达芬奇）的任何功能、设置、操作方法时触发
---

# DaVinci Resolve 参考手册技能

## 用途

当 Arden 询问 DaVinci Resolve 的任何功能、操作方法、设置参数时，快速检索官方手册内容，给出准确答案。

## 知识库

- **索引量**：8,684 个知识块，206 个章节
- **来源**：
  - DaVinci Resolve 20.3 Reference Manual（4300 页）
  - DaVinci Resolve 20 Reference Manual（4234 页）
  - DaVinci Resolve 21 New Features Guide（150 页）
- **语言**：英文原文（手册本身是英文）

## 检索工具

### 搜索脚本

```bash
SKILL_DIR="$HOME/.agent/skills/team_skills/davinci-ref"
python3 "$SKILL_DIR/search_knowledge.py" "<查询词>" --top N
```

- 支持中英文查询（自动分词）
- 返回 BM25 算法排序的最相关知识块
- `--top N`：返回条数（默认 8 条）
- `--json`：输出原始 JSON（供程序处理）

### 查询策略

| 问题类型 | 示例查询词 |
|---------|-----------|
| 操作方法 | `how to use retime controls`, `speed ramp`, `multicam sync` |
| 功能介绍 | `color node`, `fusion page`, `fairlight audio` |
| 设置参数 | `HDR setup`, `ACES color science`, `proxy mode` |
| 快捷键 | `keyboard shortcut`, `blade tool` |
| 中文问题 | 内部翻译成英文关键词后检索，如「调色」→ `color grading` |

### 检索流程

1. 解析用户问题，提取英文关键词
2. 调用 `search_knowledge.py` 获取最相关的 5-8 个知识块
3. 选取与问题最相关的 1-3 条，展示：
   - 章节名称（H2 标题）
   - 页面主题（H3 标题）
   - 原文内容（关键段落）
4. 用中文总结回答，注明来源章节

## 回答格式

```
回答要点（中文）：
1. [具体操作步骤或功能说明]
2. ...

来源：Chapter XX: 章节名称
原文摘要：「...相关段落...」
```

## 限制

- 知识库为英文原文，回答时翻译为中文
- 涉及具体数值参数时，优先引用原文
- 若检索结果与问题不完全匹配，注明「手册未明确说明」的部分
