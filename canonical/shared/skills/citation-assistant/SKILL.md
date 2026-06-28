---
name: citation-assistant
description: Use when the user needs academic citations, BibTeX, venue/author quality checks, help filling [CITE] placeholders, or managing a LaTeX .bib file (add/update references, fix citation format, dedupe). Triggers include 文献引用、找引用、citation、bib、参考文献、替换不规范引用、查询作者 H-index、判断期刊/会议质量、add to bibliography、更新bib、add citation、update references。
---

# Citation Assistant 学术文献引用助手

## ⚠️ 核心原则

1. **必须通过 `scripts/` 目录中的脚本执行**，禁止手动编写 curl 命令
2. **禁止使用 Tavily、WebSearch 等非学术搜索工具**进行文献检索
3. **语义优先**：理解引用意图，避免仅用关键词检索
4. **不自动修改文稿**：所有推荐需用户确认后再应用

---

## 📦 可用脚本

依赖：`curl`、`jq`、`sqlite3`

| 脚本 | 用途 | 用法 |
|------|------|------|
| `s2_search.sh` | 少量高相关结果检索（含 arXiv 判断） | `bash scripts/s2_search.sh "query" [limit]` |
| `s2_bulk_search.sh` | 批量拉取候选结果并按本地 limit 输出（含 arXiv 判断） | `bash scripts/s2_bulk_search.sh "query" "year_range" limit` |
| `author_info.sh` | 作者信息查询（H-index） | `bash scripts/author_info.sh "author_id"` |
| `venue_info.sh` | 期刊综合查询 | `bash scripts/venue_info.sh "venue_name"` |
| `ccf_lookup.sh` | CCF 分级查询 | `bash scripts/ccf_lookup.sh "venue_name"` |
| `if_lookup.sh` | 影响因子查询 | `bash scripts/if_lookup.sh "journal_name"` |
| `doi2bibtex.sh` | DOI 转 BibTeX | `bash scripts/doi2bibtex.sh "doi"` |
| `crossref_search.sh` | CrossRef 搜索（fallback） | `bash scripts/crossref_search.sh "query" [limit]` |

---

## 🆕 增强功能

### arXiv 文章智能判断

搜索结果会自动标记 arXiv 文章的引用状态：

| 状态 | 条件 | 推荐建议 |
|------|------|----------|
| `recommended` | arXiv + 引用 ≥ 100 | ✅ 高影响力 arXiv，可引用 |
| `caution` | arXiv + 引用 < 100 | ⚠️ 低引用 arXiv，谨慎引用 |
| `normal` | 正式发表 | ✅ 正式发表 |

**配置引用阈值**（默认 100）：
```bash
export ARXIV_CITATION_THRESHOLD=100
```

### 作者信息查询

搜索结果包含前 3 位作者的 ID，可用于查询 H-index：

```bash
# 查询作者 H-index、总引用量、论文数
bash "${CLAUDE_SKILL_ROOT}/scripts/author_info.sh" "18119920"
```

返回示例：
```json
{
  "name": "Daquan Zhou",
  "hIndex": 25,
  "citations": 8500,
  "papers": 42
}
```

---

## 🔄 工作流程

### Step 1: 解析需求

识别用户需求类型：
- **[CITE] 占位符**：提取上下文，构造语义查询
- **替换不规范引用**：分析原文引用的语义意图
- **期刊查询**：直接查询 CCF/IF 数据库
- **作者质量评估**：查询第一/通讯作者的 H-index

### Step 2: 语义化查询构造

| 引用目的 | 查询策略示例 |
|----------|--------------|
| 事实背书 | "chest radiography most widely used imaging test globally statistics" |
| 方法引用 | "attention mechanism transformer neural machine translation" |
| 背景介绍 | "deep learning medical image analysis survey review" |

### Step 3: 执行搜索

- 需要少量高相关结果时，优先使用 `s2_search.sh`
- 需要减少请求次数、批量拉取候选结果并再做筛选时，使用 `s2_bulk_search.sh`

```bash
# 少量高相关结果
bash "${CLAUDE_SKILL_ROOT}/scripts/s2_search.sh" "YOUR_QUERY" 10

# 批量候选结果（bulk endpoint），再由脚本按 limit 输出前 N 条
bash "${CLAUDE_SKILL_ROOT}/scripts/s2_bulk_search.sh" "YOUR_QUERY" "2020-" 20
```

**如果返回 429 错误**，使用 CrossRef fallback：
```bash
bash "${CLAUDE_SKILL_ROOT}/scripts/crossref_search.sh" "YOUR_QUERY" 20
```

### Step 4: 评估文献质量

```bash
# 查询期刊质量
bash "${CLAUDE_SKILL_ROOT}/scripts/venue_info.sh" "Nature Medicine"

# 查询作者 H-index
bash "${CLAUDE_SKILL_ROOT}/scripts/author_info.sh" "AUTHOR_ID"
```

### Step 5: 生成 BibTeX

```bash
bash "${CLAUDE_SKILL_ROOT}/scripts/doi2bibtex.sh" "10.1038/s41591-020-0792-9"
```

### Step 6: 生成中文推荐报告

输出格式示例：

```markdown
## 引用推荐报告

### [CITE] 位置 1

**原文上下文**：
> In chest radiography---arguably the most widely used imaging test globally [CITE]---

**推荐文献**：

#### 推荐 1: Wu2020 - CheXpert: A large chest radiograph dataset...

**质量指标**：
| 维度 | 值 | 说明 |
|------|-----|------|
| CCF 分级 | N/A | 非CS领域期刊 |
| JCR 分区 | Q1 | 顶级医学影像期刊 |
| 影响因子 | 29.1 | 极高影响力 |
| 引用量 | 3500+ | 高被引文献 |
| arXiv 状态 | normal | 正式发表 |

**推荐理由**：顶级期刊发表，直接支持原文论点。

**BibTeX**：
```bibtex
@article{Wu2020, ... }
```

**建议用法**：将 `[CITE]` 替换为 `~\cite{Wu2020}`
```

---

## 📚 .bib 文件管理（BibTeX 增删改）

当用户要往 `.bib` 文件里增/改条目、修引用格式、去重时使用。触发：`add to bibliography` / `更新bib` / `add citation` / `update references` / "修引用格式"。

### 流程

1. 确定来源：Zotero item key、DOI（用 `scripts/doi2bibtex.sh` 转 BibTeX）、或手写 BibTeX
2. 在目标 `.bib` 文件里查重（见下方查重规则）
3. 按约定生成 citation key
4. 校验 BibTeX 语法（见下方校验清单）
5. 追加到 `.bib` 文件
6. 返回 citation key 供文稿使用

### 输入

- **来源**：Zotero item key / DOI / 手写 BibTeX
- **目标 .bib 文件**：路径
- **citation key 偏好**（可选）：自定义 key 格式

### Citation Key 约定

格式：`{FirstAuthorLastName}{SecondAuthorLastName}{Year}`

| Authors | Example Key |
|---------|-------------|
| Single author | `Smith2024` |
| Two authors | `SmithJones2024` |
| Three+ authors | `SmithEtAl2024` |

冲突时追加字母：`Smith2024a`, `Smith2024b`

### 查重（写入前必做）

在已有 `.bib` 中搜索：
1. **同 DOI** — 精确命中 → 跳过并提示
2. **同标题** — 模糊匹配 (>90%) → 警告用户
3. **同 author+year+venue** — 疑似重复 → 警告用户

### 必填字段

| 类型 | 必填字段 |
|------|----------|
| `@article` | author, title, journal, year |
| `@inproceedings` | author, title, booktitle, year |
| `@book` | author/editor, title, publisher, year |
| `@misc`（arXiv） | author, title, year, eprint, archiveprefix |

### 语法校验清单

- [ ] entry 类型合法（@article, @inproceedings 等）
- [ ] 必填字段齐全
- [ ] 字段内无未转义特殊字符
- [ ] 大括号配对
- [ ] year 为数字
- [ ] pages 格式正确（如 `123--145`）

### 常见自动修正

- `pages = {123-145}` → `pages = {123--145}`
- 转义特殊字符：`&` → `\&`
- 规范作者格式：`Last, First and Last, First`
- 去掉字段尾逗号

### 从 Zotero 取 BibTeX

```python
# Get BibTeX from Zotero item
zotero_get_item_metadata(item_key="ABC123", format="bibtex")
```

### 输出格式

```markdown
## Added Entry

```bibtex
@article{SmithJones2024,
  author = {Smith, John and Jones, Jane},
  title = {A Novel Approach to Something Important},
  journal = {Journal of Important Research},
  year = {2024},
  doi = {10.1234/example.2024}
}
```

## Citation Key
`SmithJones2024`

## Usage in LaTeX
```latex
\cite{SmithJones2024}
```

## Validation
- [x] BibTeX syntax valid
- [x] No duplicate entry found
- [x] Required fields present
```

### 校验失败

```markdown
## Validation Error

**Issue**: Missing required field 'journal' for @article
**Entry**: SmithJones2024

**Suggested Fix**: Add journal field or change to @misc for preprints
```

---

## ⚙️ 配置

### Semantic Scholar API Key（强烈推荐）

```bash
# 在 Skill 目录创建 .env 文件
echo 'S2_API_KEY="your_key_here"' > "${CLAUDE_SKILL_ROOT}/.env"

# 获取 API Key: https://www.semanticscholar.org/product/api/api-key
```

| 模式 | 速率限制 | 推荐场景 |
|------|----------|----------|
| 有 API Key | 1 次/秒 | 日常使用（推荐） |
| 无 API Key | 共享限额 | 极易触发 429 |

### arXiv 引用阈值（可选）

```bash
# 默认 100，可在 .env 中配置
echo 'ARXIV_CITATION_THRESHOLD=100' >> "${CLAUDE_SKILL_ROOT}/.env"
```

---

## 🚨 错误处理

### 429 Rate Limit

1. 等待 1-2 秒后重试
2. 使用 `s2_bulk_search.sh`
3. 使用 `crossref_search.sh`（无严格限制）

### 无搜索结果

1. 简化关键词
2. 使用英文查询
3. 尝试 CrossRef fallback

---

## 📊 质量评估维度

| 维度 | 权重 | 计算 |
|------|------|------|
| CCF 分级 | 基础分 | A=100, B=70, C=40 |
| JCR 分区 | 基础分 | Q1=80, Q2=60, Q3=40, Q4=20 |
| 中科院分区 | 基础分 | 1区=90, 2区=70, 3区=50, 4区=30 |
| 影响因子 | 30% | IF × 5 (上限50) |
| 引用量 | 20% | log₁₀(citations+1) × 10 (上限50) |
| 年份 | 10% | (year-2015) × 2 (上限30) |
| 作者 H-index | 10% | 第一作者 H-index × 2 (上限30) |

**arXiv 处理**：
- 引用 ≥ 100：正常评分
- 引用 < 100：降低优先级 (-20 分)
- 有正式发表版本优先
