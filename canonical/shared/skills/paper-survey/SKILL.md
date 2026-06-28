---
name: paper-survey
description: |
  从 Zotero collection 读取论文，按 tag 分类，逐篇生成详细总结，保存到 Obsidian。
  每次只处理一个分类（tag），每篇论文根据体裁（survey/benchmark/method）用不同模板总结。

  触发词："文献综述"、"literature review"、"帮我写综述"、"review 一下这个 collection"、
  "综述报告"、"帮我整理文献"
---

> **开始前**: 先说一声 "开始文献综述 📖"

# 文献综述 (Literature Review)

从 Zotero collection 读取论文，按 tag 分类，**每次只处理一个分类**，对该分类下的每篇论文逐一写详细总结。

## Step 0: 读取共享配置

读取 `../_shared/user-config.json`（和 local 覆盖），获取：
- `VAULT_PATH`（Obsidian vault 路径）
- `NOTES_PATH`（论文笔记目录）
- `zotero_db`（Zotero 数据库路径）

## Step 1: 确认参数

每次 review 前**必须**与用户确认：

| 参数 | 说明 | 示例 |
|------|------|------|
| Zotero collection | 要 review 的 collection | "Agent Memory UX/Personalization" |
| 分类 (tag) | 本次要 review 哪个 tag | "topic:memory-benchmark" |
| Obsidian 保存路径 | 报告保存位置 | `{VAULT_PATH}/文献综述/` |

先展示该 collection 下所有 tag 及其论文数量，让用户选择：

```
该 collection 共 157 篇论文，tag 分布：
  topic:memory-architecture    75 篇
  topic:personalization        84 篇
  topic:memory-benchmark       55 篇
  topic:conversation          112 篇
  ...
你想 review 哪个分类？
```

## Step 2: 拉取论文数据

从 Zotero 获取该分类下所有论文的元数据（标题、作者、摘要、tags、日期、链接）。

**优先使用 MCP 工具**（Zotero 运行中）：
```
mcp__zotero__zotero_search_by_tag(tag=["topic:memory-benchmark"], limit=200)
```

**备选**（MCP 503 时，Zotero 关闭后用 SQLite）：
```python
conn = sqlite3.connect("~/Zotero/zotero.sqlite")
# 通过 itemTags → tags → items → itemData 查询
```

## Step 3: 获取论文全文

对每篇论文，尝试获取 PDF 全文用于详细总结：

1. **优先**：`mcp__zotero__zotero_get_item_fulltext(item_key)` 获取 Zotero 索引的全文
2. **备选**：通过 arXiv URL 下载 PDF，用 `/paper-read` 读取
3. **最低限度**：仅用摘要（在总结中标注"基于摘要"）

## Step 4: 逐篇写总结

对该分类下的每篇论文，根据其 **type tag** 使用不同模板写详细总结。

用户通常按体裁分批阅读（先 benchmark → 再 survey → 最后 method），每种体裁需要关注的信息不同，因此使用针对性模板。

所有模板共享的**通用头部**：

```markdown
---

## {论文标题}

**链接**：[arXiv]({url}) | [PDF]({pdf_url})
**作者**：{完整作者列表}
**机构**：{主要机构}
**发布时间**：{date}
**Tags**：{所有 tags}

> 一句话总结：{用一句话概括这篇论文做了什么、核心发现是什么}

### 核心贡献
1. **贡献1**：{...}
2. **贡献2**：{...}
3. **贡献3**：{...}（如有）
```

以下是每种体裁的**专属章节**（接在通用头部之后）：

### Benchmark / Dataset 模板

```markdown
### 问题定义
{定义了什么问题？评测的是什么能力？与现有 benchmark 的核心区别？}

### 现有方法的局限
{为什么需要新 benchmark？现有评测手段的不足}

### 环境与数据集
{评测环境描述、数据来源/构造方式、规模、质量控制方法}

| 维度 | 详情 |
|------|------|
| 数据来源 | {人工/自动/半自动} |
| 规模 | {N 个实例/用户/任务} |
| 特点 | {多轮/多会话/交互式/...} |

### 评测模型
{比较了哪些模型/系统？包括哪些 baseline？}

### 评测指标 (Metrics)
| 指标 | 衡量什么 |
|------|----------|
| {metric1} | {...} |
| {metric2} | {...} |

### 主要结论
{关键实验发现，量化数据，排名}

### 批判性思考
**优点**：{这个 benchmark 做得好的地方}
**局限性**：{覆盖不到的场景、设计上的限制}
**潜在改进**：{如何可以做得更好}

### 相关工作
| 论文/Benchmark | 关系 | 与本文区别 |
|----------------|------|-----------|
| {work1} | {竞品/前序} | {...} |

---
```

### Survey 模板

```markdown
### 分类体系
{这篇 survey 把领域分成了哪几类？用了什么分类维度/taxonomy？}

| 类别 | 代表方法 | 特点 |
|------|----------|------|
| {...} | {...} | {...} |

### 各类方法概览
{每个类别下的代表性方法和核心思路}

### 关键方向与趋势
{survey 指出了哪些重要方向？作者认为什么是未来趋势？}

### 开放问题
{survey 识别的尚未解决的问题}

### 批判性思考
**优点**：{覆盖全面性、分类合理性}
**局限性**：{遗漏的方向、分类是否过粗/过细}
**潜在改进**：{可以补充的视角}

### 相关工作
| 相关 Survey | 覆盖范围 | 与本文区别 |
|-------------|----------|-----------|
| {...} | {...} | {...} |

---
```

### Method 模板

```markdown
### 问题背景
**要解决的问题**：{...}
**现有方法的局限**：{...}
**本文的动机**：{...}

### 方法详解

**整体框架**：
{用文字描述整体流程，如：输入 → 模块A → 模块B → 输出}

**核心模块**：
{每个关键模块的设计和作用}

**关键技术细节**：
{损失函数、训练策略、推理流程等，视论文内容而定}

### 实验

| 数据集/环境 | 规模 | 特点 |
|-------------|------|------|
| {...} | {...} | {...} |

**主要结果**：{关键量化结果，与 baseline 的对比}

**消融实验**：{哪些组件最重要？去掉什么影响最大？}

### 批判性思考
**优点**：{方法的新颖性、实用性}
**局限性**：{假设条件、适用范围、scalability}
**潜在改进**：{可以怎么改进或扩展}

### 相关工作
| 论文 | 关系 | 说明 |
|------|------|------|
| {...} | {baseline/改进/启发} | {...} |

### 后续阅读
- [ ] {值得进一步阅读的相关论文}

---
```

### Framework / System 模板

```markdown
### 问题背景
**要解决的问题**：{...}
**现有方案的局限**：{...}

### 系统设计

**整体架构**：
{系统由哪些模块组成，整体流程}

**关键组件**：
{每个模块的功能和设计选择}

**与现有框架的区别**：
{对比 Mem0、MemGPT 等已有框架}

### 评测/验证
{如何验证框架有效性？在哪些任务上测试？}

### 批判性思考
**优点**：{设计的合理性、通用性}
**局限性**：{适用场景、工程复杂度}
**潜在改进**：{...}

---
```

### Analysis 模板

```markdown
### 研究问题
{这篇分析研究了什么问题？}

### 实验设计
{如何设计实验来回答研究问题？}

### 关键发现
1. {发现1}
2. {发现2}
3. {发现3}

### 对后续研究的启示
{这些发现对 memory 系统设计有什么指导意义？}

### 批判性思考
**优点**：{分析的深度、方法的严谨性}
**局限性**：{实验范围、结论的泛化性}

---
```

### 关键图片提取

**默认不配图**。图片提取耗时较长，仅在用户明确要求时才执行（如"带图"、"配图"、"要图片"）。模板中的 `### 关键图表` 章节在不配图时直接省略。

当用户要求配图时，使用以下方法：

**方法：基于 pymupdf (fitz) 的页面区域裁切**

学术论文的框架图通常是矢量绘制的，不会作为单独图片嵌入 PDF，因此 `pdfimages` 提取的往往是小碎片（图标、截图等）。正确做法是：

```python
import fitz

def crop_figure(pdf_path, page_num, crop_frac, output_path, dpi=250):
    """
    从 PDF 指定页面裁切出 figure 区域。
    crop_frac: (x0, y0, x1, y1) 页面比例坐标 (0-1)
    """
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    pw, ph = page.rect.width, page.rect.height
    x0, y0, x1, y1 = crop_frac
    clip = fitz.Rect(x0*pw, y0*ph, x1*pw, y1*ph)
    mat = fitz.Matrix(dpi/72, dpi/72)
    pix = page.get_pixmap(matrix=mat, clip=clip)
    pix.save(output_path)
```

**定位 figure 的步骤**：
1. 用 `page.search_for("Figure 1")` 找到 caption 的 y 坐标
2. Figure 通常在 caption **上方**，裁切从 caption 往上到合理位置
3. 双栏论文注意 x 范围（左半页 0-0.5 或右半页 0.5-1.0，跨栏则 0-1.0）

**保存位置**：`{VAULT_PATH}/attachments/lit_review/{paper_id}_fig{N}.png`

**在 markdown 中引用**（Obsidian 格式）：`![[attachments/lit_review/{paper_id}_fig{N}.png]]`

**注意事项**：
- `pdfimages` 和 `extract_image()` 只能提取嵌入式位图，对矢量图无效，不要依赖
- 不要用 `pdftoppm` 截取整页作为 figure，粒度太粗
- 如果 PDF 不可用，标注"图片待补充"

## Step 5: 组装报告

将所有论文总结组装成一个完整的 markdown 文件：

```markdown
---
title: "文献综述：{collection} / {tag}"
date: {today}
source: Zotero/{collection}
tag: {tag}
total_papers: {N}
---

# {tag 名称} 文献综述

> 生成时间：{date} | 论文数：{N} 篇 | 来源：Zotero `{collection}` | 分类：`{tag}`

## 概览

{该分类的整体概述：这些论文在解决什么大问题？有几种技术路线？时间分布如何？}

### 体裁构成
| 体裁 | 数量 |
|------|------|
| type:method | X |
| type:benchmark | Y |
| type:survey | Z |
| ... | ... |

---

{逐篇论文总结，按时间倒序排列}

## {论文1 标题}
...（完整模板内容）

## {论文2 标题}
...

...

---

## 总结与开放问题

{基于所有论文的整体分析：}
- 当前该分类的主要技术路线有哪些？
- 各路线的优劣势？
- 尚未被充分探索的方向？
```

## Step 6: 保存到 Obsidian

保存路径：`{VAULT_PATH}/文献综述/{collection_name}/{tag_name}_{date}.md`

图片保存到：`{VAULT_PATH}/attachments/lit_review/`

同时更新 review 历史记录（用于追踪哪些分类已 review 过）：
```json
// {VAULT_PATH}/文献综述/_review_history.json
{
  "reviews": [
    {
      "date": "2026-03-16",
      "collection": "Agent Memory UX/Personalization",
      "tag": "topic:memory-benchmark",
      "paper_count": 55,
      "report_path": "文献综述/Agent_Memory/topic_memory-benchmark_2026-03-16.md"
    }
  ]
}
```

## Step 7: 完成汇总

- 报告保存到 `{path}`
- 本次 review：{tag} 分类，共 {N} 篇论文
- 体裁分布：method X 篇, benchmark Y 篇, survey Z 篇
- 图片提取：{M} 张
- 提示用户可继续 review 其他分类

## 注意事项

- **尽可能自动完成，减少中断用户**：用户可能不在电脑旁，整个 review 过程中遇到的文件操作、目录创建、依赖安装（如 pymupdf）、PDF 下载等问题都应自动解决，不要停下来问用户。只有在需要用户做关键决策时（如选哪个 tag）才中断。
- **每次只处理一个分类**，不要一次性 review 所有分类
- 每篇论文都要详细总结，不是综合概述
- 不同体裁用不同模板，确保覆盖该体裁最关键的信息
- 图片是重要的信息载体，尽量提取关键图表
- 论文按时间倒序排列（最新的在前）
- 如果某分类论文太多（>30），建议和用户确认是否分批处理，或只处理高分论文
- 已有 Obsidian 笔记的论文用 `[[笔记名]]` 链接，但仍然写完整总结（因为笔记格式可能不同）
- **并行 agent 超过 3 分钟无进度或反复报错时，立即切换到主进程逐批处理**（每 5 篇一批，写完立即追加保存），不要反复重试 agent
- **用户可能需要英文版** share 给 coworker：同一份报告生成中英双版本，英文版文件名加 `_en` 后缀
- **context 管理**：29 篇全文一次性读入会撑爆 context。每批读 5 篇全文 → 写总结 → 追加保存 → 继续下一批
