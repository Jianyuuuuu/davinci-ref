# davinci-ref

> DaVinci Resolve 官方手册知识库 — 让 AI 助理秒懂达芬奇

[davinci-ref](https://github.com/Jianyuuuuu/davinci-ref) 把 Blackmagic Design 官方发布的 DaVinci Resolve 参考手册（新功能指南、用户手册）转换成可检索的知识库，接入任何支持 Skill 扩展的 AI 助理应用后，直接用自然语言提问即可获得准确的官方解答。

---

## 功能

- **自然语言问答**：用中文或英文提问，搜索官方手册原文
- **来源可溯**：每条回答都标注来自哪个章节，可自行查阅原文档
- **离线可用**：知识库为本地 JSON 文件，无需联网
- **无门槛接入**：Clone 后运行一条命令即可重建索引

---

## 知识库规模

| 文档 | 版本 | 页数 |
|------|------|------|
| DaVinci Resolve 20.3 Reference Manual | 20.3 | 4300 |
| DaVinci Resolve 20 Reference Manual | 20 | 4234 |
| DaVinci Resolve 21 New Features Guide | 21 | 150 |

**总计：8684 个知识块，206 个章节**

---

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/Jianyuuuuu/davinci-ref.git
cd davinci-ref
```

### 2. 安装依赖

```bash
# Python 3.10+
pip install pypdf
```

### 3. 重建索引（可选，预编译索引已包含在仓库中）

如需从原始 PDF 重新构建知识库：

```bash
# 下载 DaVinci Resolve 官方 PDF 并放到同一目录
python index_knowledge.py
```

---

## 使用方法

### 命令行检索

```bash
python search_knowledge.py "speed ramp" --top 5
python search_knowledge.py "voice convert" --top 3
python search_knowledge.py "HDR setup" --top 3
```

### 接入 AI 助理（OpenClaw Skill）

把仓库放置到 AI 助理的 skills 目录，例如：

```bash
cp -r davinci-ref ~/.agent/skills/team_skills/
```

在支持 OpenClaw 的应用中即可直接用自然语言提问：

- "Speed Ramp 怎么做？"
- "Retime Controls 是什么？"
- "Voice Convert 怎么用？"
- "如何设置 HDR 输出？"

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `SKILL.md` | Skill 说明文档（接入指南、检索方法） |
| `search_knowledge.py` | 检索脚本（BM25 排序） |
| `index_knowledge.py` | 索引构建脚本（从 Markdown 切块） |
| `knowledge_index.json` | 预编译知识库索引（8684 块，4.4 MB） |

---

## 工作原理

1. **PDF → 结构化 Markdown**：将官方 PDF 按页拆分，清除页眉页脚，保留原始文字
2. **分块（Chunking）**：按章节（H2）和页面（H3）组织，每 200 行切分
3. **BM25 检索**：对查询词进行中英文分词，返回相关性最高的知识块

---

## 知识库来源

本知识库内容来自 Blackmagic Design 官方发布的 DaVinci Resolve 参考手册，均为英文原文。本项目仅做结构化处理，不对原文做任何修改或删减。

---

## 许可证

知识库内容版权归 Blackmagic Design 所有。本项目（索引脚本、检索代码）采用 MIT 许可证。
