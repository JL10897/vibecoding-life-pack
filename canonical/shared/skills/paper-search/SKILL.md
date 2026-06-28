---
name: paper-search
description: |
  针对特定领域批量检索 arXiv 论文，用户筛选后导入 Zotero 并自动打标签。
  支持自定义关键词、时间范围（天/月）、arXiv 分类。

  触发词："论文检索"、"paper search"、"帮我搜论文"、"检索最近N个月的论文"、
  "这个领域最近有什么论文"、"批量检索论文"
---

> **开始前**: 先说一声 "开始论文检索 🔍"

# 论文检索 (Paper Search)

针对特定研究领域，批量检索 arXiv 论文，打分筛选后让用户挑选，选中的导入 Zotero 并自动打标签归类。

**本 skill 的终点是 Zotero 导入 + 打标签**。如需对导入的论文做文献综述，使用 `/paper-survey`。

## Step 0: 读取共享配置

先读取 `../_shared/user-config.json`，如果 `../_shared/user-config.local.json` 存在，再用它覆盖默认值。

获取以下变量备用：
- `VAULT_PATH`
- `NOTES_PATH`
- `KEYWORDS`（默认关键词）
- `NEGATIVE_KEYWORDS`
- `ARXIV_CATEGORIES`

## Step 1: 确认检索参数

与用户确认以下参数（如果用户已在指令中给出则直接使用）：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| 时间范围 | 几天/几个月 | 用户指定，无默认 |
| 关键词 | 正向筛选词 | 共享配置中的 keywords |
| 负向关键词 | 排除词 | 共享配置中的 negative_keywords |
| arXiv 分类 | 搜索范围 | 共享配置中的 arxiv_categories |
| 返回数量 | 最多返回几篇 | 100 |
| Zotero collection | 导入到哪个 collection | 用户指定 |

如果用户说了具体领域但没给关键词列表，帮用户把领域描述转化为关键词列表，并确认。

## Step 2: 批量抓取

**不要使用 `survey_fetch.py` 的按分类浏览模式**（数据量太大会触发 429/503）。直接用 arXiv API 关键词搜索：

```python
# arXiv 关键词搜索（空格编码为 +，不用引号短语）
url = f"https://export.arxiv.org/api/query?search_query=all:keyword1+AND+all:keyword2&sortBy=submittedDate&sortOrder=descending&start=0&max_results=100"
```

每组查询间隔 4 秒，每组最多 2 页（200 篇），SSL 错误最多重试 3 次后跳过。

## Step 3: 展示推荐列表

读取结果，按分数降序展示。每个分组最多显示 20 篇。

## Step 4: 用户挑选

生成带 checkbox 的 markdown 文件 `survey_pick.md`，保存到用户工作目录：

```markdown
# {领域} 论文筛选

勾选想保存到 Zotero 的论文，完成后告诉 Claude "好了"。

## 🔥 高相关 (≥5分) — N 篇
- [ ] **[8分]** Paper Title — Author1, Author2 et al. (2026-01-15) [link](url)
```

用户也可以直接口头指定编号。

**解析勾选结果**：用户说"好了"后，读取文件，提取 `[Y]` 或 `[x]` 行。注意解析用户的附加注释（如 "非常相关"），用于理解偏好并做补充搜索。

## Step 5: 导入 Zotero + 打标签

分两阶段：

### 5a: 导入（Zotero 运行中）

```bash
python3 zotero_import.py --from-json /tmp/survey_selected.json
```

### 5b: 打标签 + 归入 collection（Zotero 关闭）

告知用户："标签和分类需要操作数据库，请先关闭 Zotero，完成后再打开验证。"

确认 Zotero 已关闭（`curl -s http://127.0.0.1:23119/connector/ping` 无响应）后，通过 SQLite 操作：

```python
conn = sqlite3.connect("~/Zotero/zotero.sqlite")
# 按标题匹配 itemID → 写入 tags/itemTags → 写入 collectionItems
conn.commit(); conn.close()
```

**建议先打一篇让用户确认效果，再批量处理。**

标签体系分两个维度（根据标题+摘要关键词自动判断）：

**体裁**：`type:method` | `type:benchmark` | `type:dataset` | `type:survey` | `type:analysis`

体裁判断规则（按贡献层判断，不是关键词匹配）：
- `type:benchmark`：标题含 benchmark/bench/eval，**或**摘要中明确说 "we introduce/propose a benchmark/dataset/evaluation"。仅在 benchmark 上测试不算。
- `type:dataset`：明确构建并发布了新数据集作为核心贡献
- `type:survey`：标题/摘要明确是 survey/review/taxonomy
- `type:method`：提出新方法/模型/框架/系统（默认类别）
- `type:analysis`：实证分析/对比研究，不提出新方法
- 一篇论文可以有多个 type tag（如既提出 method 又构建了 benchmark），但必须每个都符合上述"核心贡献"标准

**内容**：`topic:*`（根据领域动态定义，如 `topic:personalization`、`topic:memory-architecture` 等）

**重要**：导入 Zotero 时务必同时写入 abstract，否则后续打 tag 和 literature review 都缺少关键信息。zotero_import.py 的 connector API 导入可能不会自动抓取 abstract，需要在 SQLite 阶段补充。

## Step 6: 完成汇总

- 共检索 N 篇，用户选中 M 篇
- Zotero 导入成功 X 篇
- 标签分布汇总
- 提示用户可使用 `/paper-survey` 对导入的论文做综述

## 关键经验教训

### arXiv API
- 空格必须编码为 `+`，不能有裸空格
- 不支持 `all:"multi+word+phrase"` 格式（返回 400），拆成 `all:multi+AND+all:word`
- 不要按分类全量拉取，直接关键词搜索
- SSL EOF 错误属临时故障，最多重试 3 次

### Zotero
- **严禁在 Zotero 运行时直接修改 SQLite**：会导致数据库损坏
- Zotero local API (port 23119) 只读，不支持 PATCH/PUT/POST
- 写入操作只能：connector API 导入 | Zotero 关闭时操作 SQLite

### 用户筛选
- Checkbox markdown 是最佳交互方式
- 用户标注包含偏好信号，据此做补充搜索
- 多轮搜索比一次性搜索效果好
