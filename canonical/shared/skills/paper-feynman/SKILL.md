---
name: paper-feynman
description: |
  费曼式论文精读：获取全文+补充材料，交互式深度问答，最后生成笔记。
  适用于需要逐段理解、反复追问的深度阅读场景。

  触发词："费曼阅读"、"精读"、"精读一下"、"feynman reading"、"深度阅读"、
  "我要仔细读一下"、"帮我精读"、"feynman 这篇"

  与 paper-read 的区别：paper-read 是模板驱动的笔记生成（自动产出结构化笔记），
  费曼阅读是对话驱动的深度理解（用户提问 → 精确回答 → 最后凝练成笔记）。
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch, WebSearch
---

> **开始前**: "进入费曼精读模式 🔬 — 我会先获取全文，然后你随时提问，最后我帮你整理笔记。"

# 费曼论文精读 (Feynman Paper Reading)

以「费曼学习法」为核心：通过向别人解释来检验自己是否真正理解。用户提问，助手基于论文原文精确回答，力求零幻觉。

## Step 0: 读取共享配置

先读取 `../_shared/user-config.json`，如果 `../_shared/user-config.local.json` 存在，再用它覆盖默认值。

显式生成并在后续统一使用这些变量：

- `VAULT_PATH`
- `NOTES_PATH`
- `CONCEPTS_PATH`
- `ZOTERO_DB`
- `ZOTERO_STORAGE`
- `AUTO_REFRESH_INDEXES`
- `GIT_COMMIT_ENABLED`
- `GIT_PUSH_ENABLED`

其中：

- `NOTES_PATH = {VAULT_PATH}/{paper_notes_folder}`
- `CONCEPTS_PATH = {NOTES_PATH}/{concepts_folder}`
- `GIT_PUSH_ENABLED` 只有在 `GIT_COMMIT_ENABLED=true` 时才可能为真

后续统一使用上面的变量。

---

## Phase 1: 获取全文 + 补充材料

### 1.1 接收论文

**用户会自行下载 PDF 并提供路径**，skill 直接读取即可，不要自行搜索。

| 输入方式 | 示例 | 处理方法 |
|----------|------|----------|
| **用户提供路径**（主要方式） | `/Users/JL/Zotero/storage/3SA65XKC/paper.pdf` | **直接 Read，不做任何搜索** |
| arXiv 链接 | `https://arxiv.org/abs/xxxx` | WebFetch（仅用户明确给链接时） |

> ⚠️ **禁止主动搜索 PDF**。用户会提供文件路径或 Zotero storage 路径，直接读取即可。不要调用 zotero_helper、WebSearch、或其他搜索手段去"找"论文，这会浪费大量时间。

### 1.2 读取全文

1. 用户提供路径 → 直接 `Read` PDF
2. 如果用户提供的是 Zotero storage 目录（如 `/Users/JL/Zotero/storage/XXXX/`），用 `ls` 找到其中的 PDF 文件再 Read
3. 精读模式下**必须获取全文**。如果 Read 失败，告知用户路径有问题，让用户重新提供

### 1.3 补充材料（Supplementary）

主文由用户提供，但**补充材料需要主动搜索**，因为用户下载时不一定会注意到。

1. **arXiv 页面检查**: WebFetch `https://arxiv.org/abs/{arxiv_id}` → 检查是否有 Supplementary Material 或 Appendix
2. **项目主页**: 从论文中提取 GitHub / project page URL → 查找 supplementary PDF、附录、技术报告
3. **会议官网**: 如 CVPR/NeurIPS/ICLR 等，搜索 `"{论文标题}" supplementary site:openaccess.thecvf.com` 或 `site:openreview.net`
4. **OpenReview**: 对于 ICLR/NeurIPS，WebFetch OpenReview 页面可能有附录

> ⏱️ **补充材料搜索时间上限: 3 分钟**。快速检查上述来源，找到就提醒，找不到立即继续，不要反复尝试。

搜索完成后：
- **找到了** → 提醒用户："这篇论文还有补充材料（XX页），要不要一起看？" 并提供下载链接让用户下载后给路径
- **没找到** → 告知用户 "未找到补充材料"，继续

### 1.4 内容加载确认

全文获取完成后，向用户报告：

```
✅ 已获取：
- 主文: {论文标题} ({页数}页 / {字数}字)
- 补充材料: {有/无} ({页数}页)
- 来源: {Zotero PDF / arXiv HTML / ...}

可以开始提问了。读完后告诉我"写笔记"即可生成费曼笔记。
```

---

## Phase 2: 交互式费曼问答

### 2.1 核心原则

这是本 skill 的核心阶段。遵循以下原则：

#### 零幻觉

- **每个回答必须基于论文实际内容**，不可凭记忆或推测
- 每个关键论断**标注出处**: `(Section X)`, `(Page Y, Paragraph Z)`, `(Figure N)`, `(Table M)`, `(Eq. K)`
- 论文中**未明确说明**的内容，必须说 "论文中未提及" 或 "论文未详细展开，以下是我基于上下文的推断（非原文）"
- 引用外部知识补充背景时，**明确区分**: "📖 论文原文：..." vs "💡 背景补充（非本文内容）：..."

#### 回答风格

- **用简洁的语言解释**，像给一个聪明但不了解这个具体领域的人讲解
- 必要时用**类比**帮助理解，但类比后必须回到论文原文的精确表述
- 公式解释：逐符号拆解，解释每个变量的物理含义，不要只念一遍公式
- 图表解释：描述图表在说什么，指出关键数据点和趋势
- 如果用户的问题涉及论文中多个部分，组织回答时**标明各部分来源**

#### 行为准则

- **不催促用户**：不主动问 "还有其他问题吗"、"需要我继续解释吗"
- **不主动总结**：用户没要求就不做 "小结一下"
- **安静等待**：回答完就停，等用户下一个问题
- **允许追问**：用户可以对同一个概念反复追问，不厌其烦地换角度解释

### 2.2 内部 Q&A 追踪

在后台维护一个结构化的 Q&A 记录（不展示给用户），用于 Phase 3 笔记生成：

```
Q&A 记录格式（内部）:
- Q: {用户原始问题}
  A: {回答要点摘要}
  Refs: {Section X, Figure Y, Eq. Z}
  Topic: {归属主题，如 "方法设计"/"实验"/"理论基础"}
```

对每轮问答都更新此记录。同一主题的追问合并到一个条目下。

### 2.3 退出信号

当用户说以下任何一种时，进入 Phase 3：

- "OK了"、"可以了"、"写笔记"、"生成笔记"、"形成笔记"
- "写笔记吧"、"记录一下"、"save notes"
- "费曼笔记"、"整理一下"

---

## Phase 3: 生成费曼笔记

### 3.1 检查已有笔记

在生成前，先检查 `{NOTES_PATH}` 下是否已有该论文的笔记（由 paper-read 或其他流程生成）：

```bash
find {NOTES_PATH} -name "*.md" | head -200
# 搜索方法名或论文标题
```

- **已有笔记** → 在现有笔记末尾**追加**费曼阅读部分（用 `---` 分隔线 + `## 费曼精读笔记` 标题）
- **无已有笔记** → 创建新文件，使用完整费曼笔记模板

### 3.2 笔记模板

严格遵循 `assets/feynman-note-template.md`。

#### 新建笔记时（无已有笔记）

完整模板包含 frontmatter + 费曼笔记正文。

#### 追加到已有笔记时

在已有笔记末尾追加，格式：

```markdown

---

## 费曼精读笔记

> 精读日期: {YYYY-MM-DD}

### 核心理解

{从 Q&A 中提炼的 3-5 个最重要的理解，每个用 1-2 句话}

### 问答记录

#### {主题1: 如 "模型架构"}

**Q: {问题}**
{精炼后的回答，保留关键出处引用 (Section X, Figure Y)}

**Q: {追问}**
{精炼后的回答}

#### {主题2: 如 "训练策略"}

**Q: {问题}**
{精炼后的回答}

...

### 仍存疑的问题

- {对话中未完全解答或论文未详细说明的问题}

### 关联概念

- [[概念1]] — 在本文中的具体含义/用法
- [[概念2]] — ...
```

### 3.3 Q&A 精炼规则

将对话内容写入笔记时，做以下处理：

1. **按主题归类**: 将零散的 Q&A 按主题（方法设计、理论基础、实验分析、与其他工作对比等）重新组织
2. **合并重复**: 同一概念的多次追问合并为一个完整解答
3. **精简冗余**: 去掉对话中的寒暄、重复确认，只保留实质内容
4. **保留出处**: 所有出处引用 (Section X, Figure Y) 必须保留
5. **区分标注**: 保持 "📖 论文原文" vs "💡 背景补充" 的区分

### 3.4 关键洞察提炼

从全部 Q&A 中提炼 "核心理解" 部分，要求：

- 不是论文摘要的复述，而是**通过问答后形成的深层理解**
- 每条洞察应该是一个 "啊哈时刻" — 用户通过提问才搞明白的东西
- 3-5 条，每条 1-2 句话
- 如果某个概念用户反复追问了多次，说明它很重要，应该出现在洞察中

### 3.5 概念笔记联动

与 paper-read 保持一致：

1. **扫描**费曼笔记中所有 `[[概念]]` 链接
2. **检查**每个链接对应的概念笔记是否存在
3. **创建**不存在的概念笔记（自动归类到对应子目录）

> 分类规则和模板见 `../paper-read/references/concept-categories.md`

### 3.6 保存

#### 文件命名

与 paper-read 一致：只用**方法名/模型名** `{方法名}.md`。

#### 保存路径

按 Zotero 分类层级：`{NOTES_PATH}/{zotero_collection_path}/{方法名}.md`

如果不知道 Zotero 分类路径（如用户直接给了 PDF），保存到 `{NOTES_PATH}/_待整理/`。

#### Frontmatter（仅新建笔记时）

```yaml
---
title: "论文标题"
method_name: "MethodName"
authors: [Author1, Author2]
year: 2025
venue: arXiv
tags: [tag1, tag2]
zotero_collection: path/to/collection
reading_type: feynman
created: YYYY-MM-DD
---
```

注意 `reading_type: feynman` 字段用于区分。

#### 追加到已有笔记时

更新 frontmatter，添加 `feynman_date: YYYY-MM-DD` 字段表示精读日期。

### 3.7 保存后自动执行

1. 只有在 `AUTO_REFRESH_INDEXES=true` 时才刷新目录页：
   ```bash
   python3 ../_shared/generate_concept_mocs.py
   python3 ../_shared/generate_paper_mocs.py
   ```
2. 只有在 `GIT_COMMIT_ENABLED=true` 时才做 git：
   ```bash
   cd {VAULT_PATH} && git add {新增/修改的文件} && git commit -m "feynman reading: {方法名}"
   ```
   - 只有在 `GIT_PUSH_ENABLED=true` 且仓库已配置远端时才 push

### 3.8 完成报告

笔记保存后，向用户报告：

```
📝 费曼笔记已保存:
- 文件: {NOTES_PATH}/{path}/{方法名}.md
- 模式: {新建 / 追加到已有笔记}
- 问答记录: {N} 个问题，归为 {M} 个主题
- 核心洞察: {K} 条
- 新建概念笔记: {J} 个
```

---

## 参考文件（按需查阅，复用 paper-read 资源）

- **`../paper-read/references/zotero-guide.md`** — Zotero 查询、分类、PDF 路径获取
- **`../paper-read/references/concept-categories.md`** — 概念自动归类的 16 个子目录规则 + 模板
- **`../paper-read/assets/zotero_helper.py`** — Zotero 数据库辅助脚本
- **`assets/feynman-note-template.md`** — 费曼笔记完整模板
