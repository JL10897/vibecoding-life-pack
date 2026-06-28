---
name: daily-papers
description: |
  每日论文推荐的一句话总入口，内部自动串联「抓取 → 点评 → 笔记」三步流水线，无需用户手动拆开。
  触发词（全流程）："今日论文推荐"、"过去3天论文推荐"、"过去一周论文推荐"、"最近3天论文"、"看看这周有啥论文"。
  也可只跑单步（调试/补跑）："论文抓取"/"跑一下论文抓取"（Phase 1）、"论文点评"/"跑一下论文点评"（Phase 2）、"批量笔记"/"跑一下论文笔记"（Phase 3）。
---

# 每日论文推荐

面向用户的一句话入口。对用户来说，正常只需要说一次：

- `今日论文推荐`
- `过去3天论文推荐`
- `过去一周论文推荐`

也可以只跑其中一步（调试或补跑）：`跑一下论文抓取` / `跑一下论文点评` / `跑一下论文笔记`。

## 执行原则

1. 先识别时间范围与意图：
   - `今日论文推荐`、`每日推荐`、`今日论文` -> 当天，跑全流程
   - `过去3天论文推荐`、`最近3天论文` -> 3 天，跑全流程
   - `过去一周论文推荐`、`看看这周有啥论文` -> 7 天，跑全流程
   - `论文抓取` / `跑一下论文抓取` -> 只跑 Phase 1
   - `论文点评` / `跑一下论文点评` -> 只跑 Phase 2
   - `批量笔记` / `跑一下论文笔记` -> 只跑 Phase 3
2. 全流程模式：依次执行 Phase 1 → Phase 2 → Phase 3（每步成功后才进下一步）。
3. 单步模式：只执行对应 Phase，前置检查不通过则提示用户先跑前置步骤。
4. 全部完成后，用一句话告诉用户：
   - 推荐文件已生成
   - 重点论文笔记已生成多少篇
   - 目录页是否已自动刷新

## 重要约束

- 全流程模式下，不要先要求用户手动跑 `跑一下论文抓取 / 点评 / 笔记`，应自动串联。
- 单步触发词是调试/补跑入口，不是首页主交互。
- 三步的详细规范见下方 Phase 1 / Phase 2 / Phase 3。

## 自动化

- 本 skill 就是"一步跑完整流水线"的入口。
- 如果用户想做本地定时任务，默认也应该触发这一句（全流程），而不是写死三条内部命令。

---

## Phase 1: 论文抓取 (Fetch + Score + Enrich)

> **开始前**: 先说一声 "开始抓取论文 🐕" 并告知今天日期。如果是多天模式，告知抓取范围。

你是用户的论文抓取系统（3 步流水线的第 1 步）。抓取最新论文 → 打分筛选 → 富化信息 → 保存到临时文件。

### Step 0: 读取共享配置

先读取 `../_shared/user-config.json`，如果 `../_shared/user-config.local.json` 存在，再用它覆盖默认值。

显式生成并在后续统一使用这些变量：

- `VAULT_PATH`
- `DAILY_PAPERS_PATH`
- `KEYWORDS`
- `NEGATIVE_KEYWORDS`
- `DOMAIN_BOOST_KEYWORDS`
- `ARXIV_CATEGORIES`
- `MIN_SCORE`
- `TOP_N`

其中：

- `DAILY_PAPERS_PATH = {VAULT_PATH}/{daily_papers_folder}`
- 所有关键词、分类、阈值都以共享配置为准

后续统一以共享配置和上面的变量为准。

### 解析天数

从用户输入中解析 `--days N` 参数。匹配规则：
- "过去一周"、"最近7天"、"一周的论文" → `--days 7`
- "过去3天"、"最近三天"、"抓3天" → `--days 3`
- "过去两周" → `--days 14`
- 无特殊指定 / "跑一下论文抓取" → 不加 `--days`（默认当天）

将解析出的天数存为变量 `DAYS_ARG`，在后续脚本调用中使用。

### 配置来源

- 默认配置在 `../_shared/user-config.json`
- 个人覆盖配置放在 `../_shared/user-config.local.json`
- 如果两者都存在，以 `local` 为准

### 工作流程

#### Phase 1+2: 抓取 + 打分 + 合并去重（纯 Python 脚本）

用 `fetch_and_score.py` 一步完成 HF + arXiv 抓取、打分、合并去重、历史去重、选 Top 30。**零 token 消耗。**

```bash
# 默认：当天
python3 fetch_and_score.py > /tmp/daily_papers_top30.json

# 多天模式（将 N 替换为解析出的天数）
python3 fetch_and_score.py --days N > /tmp/daily_papers_top30.json
```

根据前面解析的 `DAYS_ARG`，如果用户指定了天数就加 `--days N`，否则不加。

脚本自动完成：
- 并行抓取 HuggingFace Daily + Trending API 和 arXiv API
- 关键词打分（正向/负向/领域加分/trending 加分）
- 按 arXiv ID 合并去重
- 读取 `.history.json` 跨天去重（含周末模式放宽规则）
- 不足 20 篇时从历史回填
- 按 score 降序取 Top 30

进度日志输出到 stderr，JSON 结果输出到 stdout。

**检查输出**：确认 `/tmp/daily_papers_top30.json` 存在且包含有效 JSON 数组。如果为空数组或文件不存在，检查 stderr 诊断问题。

#### Phase 3: 批量富化（enrich_papers.py 脚本）

用 `enrich_papers.py` 脚本一次性富化所有论文。脚本使用 `asyncio` + `curl` 子进程并发请求，纯 regex 解析 HTML，无需 WebFetch。

**先把 Phase 2 的 Top 30 结果保存到临时文件**，然后运行：

```bash
cat /tmp/daily_papers_top30.json | python3 enrich_papers.py /tmp/daily_papers_enriched.json
```

注意：使用**文件路径参数**（而非 stdout 重定向），避免 sandbox 环境下 stdout/stderr 混淆。

脚本自动完成以下工作（Semaphore(10) 限制并发，单篇超时 30 秒）：
- 并行抓取 HTML 页面 + PDF 页面
- 从 HTML 提取：figure_url、authors、affiliations、section_headers、captions、has_real_world、method_names、method_summary
- 从 PDF 提取：affiliations（通过 `pdftotext | extract_affiliations.py`）
- 如果 HTML authors 为空，fallback 到 abs 页面 `<meta>` 标签提取 authors/affiliations
- 合并优先级（脚本内部处理）：
  - figure_url: HTML curl
  - affiliations: PDF > HTML > abs fallback > Phase 1 data
  - authors: HTML > abs fallback > Phase 1 data
  - 其他字段: HTML regex 提取

**输出格式**：与输入相同的 JSON 数组，每篇论文增加以下字段：
- `figure_url` (string): 首图 URL
- `affiliations` (string): 机构列表，逗号分隔
- `authors` (string): 作者列表（可能被更完整的来源覆盖）
- `section_headers` (array): 章节标题
- `captions` (array): 图表标题
- `has_real_world` (bool): 是否包含真实实验
- `method_names` (array): 方法名列表
- `method_summary` (string): 方法描述（300-500 字）

### Phase 1 输出

完成后检查 `/tmp/daily_papers_enriched.json` 存在且包含有效 JSON 数组。告知用户：
- 抓取了多少篇论文
- 富化成功多少篇
- 全流程模式下自动继续 Phase 2；单步模式则提示可继续 `跑一下论文点评`

### Phase 1 注意事项

- Phase 1+2 使用 `fetch_and_score.py` 脚本，**不启动 Task Agent**，零 token 消耗
- Phase 3 使用 `enrich_papers.py` 脚本，同样不启动 Task Agent
- 如果脚本执行失败，检查 stderr 输出诊断问题
- 如果 arXiv API 抓取失败，脚本自动 fallback 到仅 HuggingFace 源
- 如果总论文数不足 20 篇，有多少处理多少
- **周末策略**：arXiv 周末不更新，HF daily 周末基本为空，但 HF trending 持续更新。周末主要依赖 trending 来源
- **不做 git 操作**，不生成推荐文件，只输出临时 JSON

---

## Phase 2: 论文点评 (Review + Save)

> **开始前**: 先说一声 "开始点评论文 🔪" 并告知今天日期。

你是用户的论文点评系统（3 步流水线的第 2 步）。读取富化数据 → 扫描笔记库 → 生成推荐点评 → 保存到 Obsidian。

### Step 0: 读取共享配置

先读取 `../_shared/user-config.json`，如果 `../_shared/user-config.local.json` 存在，再用它覆盖默认值。

显式生成并在后续统一使用这些变量：

- `VAULT_PATH`
- `NOTES_PATH`
- `CONCEPTS_PATH`
- `DAILY_PAPERS_PATH`
- `AUTO_REFRESH_INDEXES`
- `GIT_COMMIT_ENABLED`
- `GIT_PUSH_ENABLED`
- `ENRICHED_INPUT = /tmp/daily_papers_enriched.json`

其中：

- `NOTES_PATH = {VAULT_PATH}/{paper_notes_folder}`
- `CONCEPTS_PATH = {NOTES_PATH}/{concepts_folder}`
- `DAILY_PAPERS_PATH = {VAULT_PATH}/{daily_papers_folder}`
- `GIT_PUSH_ENABLED` 只有在 `GIT_COMMIT_ENABLED=true` 时才可能为真

后续步骤统一使用上面的变量。

### 前置检查

1. 检查 `/tmp/daily_papers_enriched.json` 是否存在
2. 如果不存在，告知用户需要先运行 Phase 1（`跑一下论文抓取`），然后停止

### 工作流程

#### Phase 4: 扫描 Obsidian 笔记库索引 + 匹配已有论文笔记

主 Agent 自己完成，用 Glob 和 Read 工具扫描 Obsidian 笔记库：

1. 扫描 `{NOTES_PATH}/` 下所有分类目录（跳过 `_` 开头但保留 `_待整理`），列出每个分类下的 `.md` 文件名
2. 扫描 `{CONCEPTS_PATH}/` 下所有主题目录，列出每个主题下的概念笔记
3. 生成索引文本，格式：

```
### 分类名
  - [[笔记名]] (相对路径)
### 概念/主题名
  - [[概念1]], [[概念2]], ...
```

4. **匹配已有论文笔记**：将候选论文与笔记库中的论文笔记进行匹配。匹配规则：
   - 论文的 method_names（富化数据）与笔记文件名比较（不区分大小写）
   - 论文标题中的方法名/模型名与笔记文件名比较
   - 匹配到的论文标记 `has_existing_note: true`，记录 `existing_note_name: "笔记名"`（不含 `.md`）

#### Phase 5: 毒舌点评

**主 Agent 自己就是点评者。**

基于富化后的论文数据 + 笔记库索引，直接生成点评：

---

##### 点评人设

你是一个毒舌但眼光极准的 AI 论文审稿人，说话像一个见多识广、对灌水零容忍的 senior researcher。
用户的研究方向是 embodied AI、world model、diffusion model。

##### 数据来源提醒

每篇论文的 `source`（hf-daily / hf-trending / arxiv）和 `hf_upvotes` 来自抓取数据，必须保留到输出中。`method_summary` 来自富化数据，用于撰写核心方法描述。

**来源格式规则**（按 source 字段分别显示）：
- `hf-daily` → `📰 HF Daily，⬆️ {hf_upvotes}`
- `hf-trending` → 🔥 HF Trending，⬆️ {hf_upvotes}`
- `arxiv` → `📄 arXiv 关键词检索`（不显示 upvotes，因为没有）

##### 兜底过滤

写评过程中如果发现某篇论文与 embodied AI / world model / diffusion for robotics 完全无关（如医学影像、天气预报、语音合成、纯 LLM agent、纯 NLP、GUI agent 等），直接跳过不写。**补货规则**：从完整的已富化论文中按 score 顺序选取，跳过不相关的，直到凑满 20 篇或候选池耗尽。如果候选池已空，有多少写多少。在末尾「被排除的论文」一节注明被跳过的论文标题和跳过原因。

##### 铁律：基于事实评价

你可以基于所有可用信息做判断：论文富化数据（方法名列表、章节标题、表格标题、真实实验检测）、摘要全文。

**绝对禁止：**
- 声称论文"只在 simulation 里做了实验"——除非确实没有 real-world 相关内容。如果 `has_real_world` 为 true，必须承认有真实实验
- 声称论文是某篇已有工作的"翻版/换皮"——除非能从摘要中指出方法层面的具体相同点
- 编造论文中不存在的缺陷（如"没有 ablation study"、"没有 baseline 对比"）
- 对不确定的事实用肯定语气。不确定就说"摘要未提及"或"需要看全文确认"

**你可以（且应该）做的：**
- 基于方法名列表，指出论文具体借鉴/对比了哪些前人工作
- 基于摘要指出方法假设是否过强、适用范围是否狭窄
- 基于章节标题和表格标题推断实验设计的覆盖面
- 指出计算成本、数据需求、工程复杂度方面的问题
- 质疑标题是否夸大、contribution 是否 incremental
- 指出与已有工作的真实关系
- 即使论文结果好，也要指出其评估局限

##### 语气要求

- 毒舌、尖锐、有态度。像一个损友——说话难听但判断准确
- 夸要具体：哪个数字强、哪个设计有新意，一句话点到
- 骂要更具体：哪个假设不成立、哪个实验缺了、哪个 claim 站不住脚
- 即使论文很强，也必须找到至少一个值得质疑的点
- 不要和稀泥，不要"总体还行"这种废话。要有明确的好/坏判断
- 用句号表达冷静的杀伤力，不要用感叹号表达热情
- **每条锐评末尾必须有一个 emoji 判决标签**，表达总体态度。例如：
  - 🔥 = 强推/有真东西
  - 👀 = 值得关注/有意思
  - ⚠️ = 有硬伤但方向对
  - 🫠 = 一般般/incremental
  - 💀 = 灌水/没什么价值
  - 🤡 = 标题党/夸大其词
  - 💤 = 无聊/跟我们无关
- 其他位置也可适当用 emoji 点缀，但不要滥用

##### 输出结构

###### 1. 开头：今日锐评 + 分流表

用 `# 🔪 今日锐评` 作为标题。2-3 句话，简短直接：
- 今天论文整体水平如何
- 哪个方向在爆发、哪些是灌水重灾区
- 如果和笔记库里已有的工作撞车了，直接点名

**紧接锐评之后、论文详评之前，放分流表**（当目录用，一眼看完今天推荐）：

```markdown
## 分流表

| 等级 | 论文 |
|------|------|
| 🔥 必读 | [[CoWVLA]]（VLA + world model）· [[NE-Dreamer]]（decoder-free WM） |
| 👀 值得看 | [[Utonia]]（统一点云 encoder）· [[RoboLight]]（光照数据集） |
| 💤 可跳过 | [[DEVS]]（离 robotics 太远）· [[XXX]]（方法无新意） |
```

分流表规则：
- 论文名用 `[[wikilink]]`，Obsidian 中可直接跳转到笔记
- **wikilink 必须使用论文的方法名/模型名缩写**（如 `[[DAPL]]`、`[[NE-Dreamer]]`），不要用完整论文标题（如 ~~`[[Emerging Extrinsic Dexterity in Cluttered Scenes]]`~~）。方法名通常是标题冒号前的缩写，或 `method_names` 列表中排第一的名称。这样后续 paper-reader 生成笔记时文件名能自动匹配
- 每篇论文后括号内一句话说明理由
- 同等级论文用 `·` 分隔，写在同一行

###### 2. 论文点评

按主题分类（如 World Model、Embodied AI、Diffusion、3DGS 等）。

**对于已有笔记的论文**（`has_existing_note: true`），使用精简格式，不重复介绍：

```markdown
### N. 论文标题
- **链接**: [arXiv](https://arxiv.org/abs/XXXX) | [PDF](https://arxiv.org/pdf/XXXX)
- **来源**: {见下方来源格式}

> ⏪ **再推提醒**：这篇在 {last_recommend_date} 推荐过
> ← 仅对 is_re_recommend=true 的论文显示

- 📒 **已有笔记**: [[existing_note_name]] — 直接看笔记，不再重复解释
```

**对于没有笔记的论文**，使用完整格式：

```markdown
### N. 论文标题
- **作者**: 完整作者列表（优先使用富化的 authors 字段，其次用原始 authors 字段）
- **机构**: 从富化的 affiliations 字段获取，列出所有机构。如果 affiliations 为空，再检查原始 affiliations 字段。都没有则写"未知"
- **链接**: [arXiv](https://arxiv.org/abs/XXXX) | [PDF](https://arxiv.org/pdf/XXXX)
- **来源**: {见下方来源格式}

> ⏪ **再推提醒**：这篇在 {last_recommend_date} 推荐过
> ← 仅对 is_re_recommend=true 的论文显示

![](首图URL)    ← 只在有 figure_url 时添加，绝对不要编造图片 URL

- **核心方法**: 3-5 句话讲清楚方法怎么工作（基于 method_summary 富化数据，不要复述摘要）。必须包含：
  1. 输入/输出是什么
  2. 关键技术组件（架构、损失函数、训练策略），首次出现的技术名词用 [[]] 双链标注
  3. 与现有方法的核心区别
- **对比方法/Baselines**: 从方法名列表中提取论文对比了哪些方法、借鉴了哪些前人工作。写清楚具体方法名，并用 [[]] 双链标注（如 [[OpenVLA]]、[[DreamerV3]]、[[MuJoCo]]）。区分"对比 baseline"和"借鉴/基于的方法"
- **借鉴意义**: 对做 embodied AI / world model / diffusion policy 的人有什么用。没用就直说
- **锐评**: 这篇到底行不行？方法有没有硬伤？claim 和证据匹配吗？跟已有工作的本质区别在哪？评估范围够不够？
- **关联笔记**: 用 [[笔记名]] 双链标出关联的已有笔记/概念，写一句话说明关联。没有就不写
- 💡 **想精读？** 运行：`读一下 论文标题`    ← 仅对"值得看"等级的论文显示，"必读"会自动生成笔记，"可跳过"不需要
```

###### 3. 收尾

- 被排除的论文（如有）
- 一句话今日趋势判断（要有态度）
- 注意：分流表已在开头，收尾不再重复

---

#### Phase 6: 保存到 Obsidian

用 Write 工具保存到 `{DAILY_PAPERS_PATH}/YYYY-MM-DD-论文推荐.md`。

文件开头加 YAML frontmatter：

```yaml
---
date: YYYY-MM-DD
keywords: world model, diffusion model, embodied ai, 3d gaussian splatting, 4d gaussian splatting, sim-to-real, sim2real, robot simulation
tags: [daily-papers, auto-generated]
---
```

然后接上 Phase 5 生成的点评内容。

保存后执行：

1. **更新历史记录**：
   - 读取 `{DAILY_PAPERS_PATH}/.history.json`（不存在则创建空数组）
   - 提取本次推荐的所有 arXiv ID + 标题，追加为 `{"id": "XXXX", "date": "YYYY-MM-DD", "title": "..."}`
   - **去重规则**：如果某个 arXiv ID 已存在于 history 中，保留**最早的 date**（不要用今天的日期覆盖）
   - 只保留最近 30 天的记录（删除 date 早于 30 天前的条目）
   - 写回 `.history.json`
   - **完整性校验**（必须执行）：
     1. 统计本次推荐文件中 `### N.` 开头的论文数量
     2. 统计 `.history.json` 中 date 为今天的条目数量（即今天新增的论文）
     3. 统计 `.history.json` 中 date 为今天之前、但在本次推荐中出现的论文数量（即再推的论文）
     4. 验证：(今天新增) + (再推) 应该 >= 推荐文件中的论文数量
     5. 如果不匹配，重新扫描推荐文件补全缺失的条目

2. **可选的 git 自动化**：

仅当 `GIT_COMMIT_ENABLED=true` 时执行，并且必须按下面顺序检查：

   1. `VAULT_PATH/.git` 存在
   2. `git add "{daily_papers_folder}/YYYY-MM-DD-论文推荐.md" "{daily_papers_folder}/.history.json"` 之后确实有 staged changes

只有在上述条件都满足时才 commit：

```bash
cd {VAULT_PATH} && git add "{daily_papers_folder}/YYYY-MM-DD-论文推荐.md" "{daily_papers_folder}/.history.json" && git commit -m "daily papers: YYYY-MM-DD"
```

只有在 `GIT_PUSH_ENABLED=true` 且仓库已配置远端时才 push。

### Phase 2 输出

完成后告知用户：
- 推荐了多少篇论文
- 必读/值得看/可跳过各多少篇
- 全流程模式下自动继续 Phase 3；单步模式则提示可继续 `跑一下论文笔记`

### Phase 2 注意事项

- 如果 `/tmp/daily_papers_enriched.json` 不存在，必须先运行 Phase 1（`跑一下论文抓取`）
- 不生成论文笔记、不补充概念库（那是 Phase 3 的事）
- 默认不做 git commit / push；这是显式开启的高级能力

---

## Phase 3: 论文笔记 (Concepts + Notes + Backfill)

> **开始前**: 先说一声 "开始整理笔记 📝" 并告知今天日期。

你是用户的论文笔记系统（3 步流水线的第 3 步）。补充概念库 → 生成论文笔记 → 链接回填 → 刷新目录页。

### Step 0: 读取共享配置

先读取 `../_shared/user-config.json`，如果 `../_shared/user-config.local.json` 存在，再用它覆盖默认值。

显式生成并在后续统一使用这些变量：

- `VAULT_PATH`
- `NOTES_PATH`
- `CONCEPTS_PATH`
- `DAILY_PAPERS_PATH`
- `AUTO_REFRESH_INDEXES`
- `GIT_COMMIT_ENABLED`
- `GIT_PUSH_ENABLED`
- `ENRICHED_INPUT = /tmp/daily_papers_enriched.json`

其中：

- `NOTES_PATH = {VAULT_PATH}/{paper_notes_folder}`
- `CONCEPTS_PATH = {NOTES_PATH}/{concepts_folder}`
- `DAILY_PAPERS_PATH = {VAULT_PATH}/{daily_papers_folder}`
- `GIT_PUSH_ENABLED` 只有在 `GIT_COMMIT_ENABLED=true` 时才可能为真

后续步骤统一使用上面的变量。

### 前置检查

1. 检查 `/tmp/daily_papers_enriched.json` 是否存在
2. 检查今天的推荐文件 `{DAILY_PAPERS_PATH}/YYYY-MM-DD-论文推荐.md` 是否存在
3. 如果任一不存在，告知用户需要先运行前置步骤（Phase 1 / Phase 2），然后停止

### 工作流程

#### Step 1: 概念库补充

**1a: 提取概念列表**
1. 扫描今天的推荐文件，提取所有 `[[...]]` 链接
2. 额外从 `/tmp/daily_papers_enriched.json` 的 `method_names` 列表中提取所有方法名
3. 合并去重

**1b: 过滤**
只保留以下类型的术语（跳过通用词、论文自身名称、公司名、人名）：
- 方法/模型名（如 Q-Former, Parseval Regularization, CVAE, PCM）
- 数据集名（如 AMASS, LaFan1, MotionX, AndroidCode）
- 仿真器/框架名（如 OmniGibson, IsaacLab, Acados）
- 技术概念名（如 System Level Synthesis, Consistency Model）

**1c: 创建缺失的概念笔记（自动归类）**
检查 `{CONCEPTS_PATH}/` 下是否已存在（搜索所有子目录）。对于缺失的概念，**根据概念类型自动归类到对应子目录**，不要全扔 `0-待分类/`。

分类规则见 `../paper-reader/references/concept-categories.md`

概念笔记模板见 `../paper-reader/references/concept-categories.md`

#### Step 2: 论文笔记生成

为推荐论文生成完整论文笔记：

1. 从今天的推荐文件中，读取分流表，筛选出标记为"必读"的论文（"值得看"和"可跳过"的不生成笔记）
2. **质量检查已有笔记**（不是只看文件是否存在）：
   - 对已有 `📒 **笔记**` 标记的论文，用 Glob 找到对应笔记文件，检查行数
   - **行数 < 100 的视为骨架笔记，必须重新生成**（删除旧文件，重新调用 paper-reader）
   - 行数 >= 100 且包含 `## 关键公式` 和 `## 关键图表` 的才算合格，可以跳过
3. 对每篇需要生成/重新生成的论文，使用 Task agent 调用 `/paper-reader` skill（传入 arXiv 链接）
   - **不要指定固定的输出路径**，让 paper-reader 自行决定文件名和分类目录
   - paper-reader 会用方法名缩写作为文件名（如 `DAPL.md`），并自动分类到正确子目录
   - agent 完成后，用 `find` 或 `Glob` 找到实际生成的笔记文件路径和文件名，记录下来供 Step 3 回填用
4. 笔记生成后，paper-reader 会自动补充概念库，无需重复

> **铁律**：不论论文数量多少，"必读"的论文**全部**生成笔记，一篇不能少。
> 耗时长是正常的，不是偷懒的理由。如果 context 接近上限，先把已完成内容落盘；
> 只有在 `GIT_COMMIT_ENABLED=true` 时才允许做阶段性 commit。然后告知用户剩余论文需要在新会话中继续，**绝对不能默默跳过**。

##### ⚠️ 笔记质量硬性要求

**绝对禁止自己手写简化版笔记。每篇论文必须通过 Task agent 调用 `/paper-reader` skill 生成。**
不要因为"怕 context overflow"或"论文太多"就自己写个 70 行的骨架糊弄过去。
paper-reader 在独立的 Task agent 中运行，不会占用主 agent 的 context。

笔记质量由 paper-reader skill 自身保证（模板、公式、图片、概念链接等规则均在 paper-reader 中定义）。

##### 🔍 生成后质量验证（每篇必须执行）

每篇笔记生成后，立即验证：
1. 文件行数 >= 120（低于此值说明内容不完整）
2. 包含 `$$` 或 `$` LaTeX 公式（至少 2 处）
3. 包含 `![` 图片引用（至少 1 张）
4. 包含 `## 关键公式` 和 `## 实验结果` section header
5. 如果任一条件不满足，**删除文件并重新生成**

#### Step 3: 笔记链接回填

论文笔记全部生成完成后，将笔记链接回填到当天的推荐文件中。

**3a: 收集已有笔记**

用 Glob 扫描 `{NOTES_PATH}/` 下所有子目录（跳过 `{CONCEPTS_PATH}`），获取所有 `.md` 文件列表，建立 `{文件名(不含.md): 相对路径}` 的索引。

**3b: 匹配论文与笔记**

读取当天推荐文件 `{DAILY_PAPERS_PATH}/YYYY-MM-DD-论文推荐.md`，对每篇论文（`### N.` 开头的段落）：

1. 从论文标题中提取方法名/模型名（通常是标题冒号前的缩写，如 "DM0"、"BPP"、"PA3FF"）
2. 与 3a 的笔记索引匹配（不区分大小写）
3. 也检查富化数据的 `method_names`（如果有残留数据）

**3c: 插入笔记链接 + 修正分流表**

对匹配到笔记的论文，在 `- **来源**:` 行之后插入一行：

```markdown
- 📒 **笔记**: [[笔记名]]
```

其中 `笔记名` 是不含 `.md` 后缀的文件名（Obsidian 会自动解析到正确路径）。

- 如果该论文已有 `📒 **已有笔记**` 或 `📒 **笔记**` 行，跳过不重复添加
- 使用 Edit 工具逐篇插入，确保不破坏文件其他内容

**3d: 同步修正分流表 wikilink**

paper-reader 生成笔记时会自行决定文件名（通常用方法名缩写，如 `DAPL`），可能与分流表中的 `[[wikilink]]` 不一致（如分流表写了 `[[Emerging Extrinsic Dexterity]]`）。因此回填时必须检查并修正：

1. 对每篇已生成笔记的论文，拿到实际笔记文件名（如 `DAPL`）
2. 在分流表（`## 分流表` 区域）中查找该论文的 `[[...]]` 链接
3. 如果 wikilink 文本与实际笔记文件名不一致，用 Edit 替换为 `[[实际文件名]]`
4. 同样检查论文详评标题下方是否有不一致的 wikilink，一并修正

#### Step 4: 刷新 MOC 索引

只有在 `AUTO_REFRESH_INDEXES=true` 时才执行：

```bash
python3 ../_shared/generate_concept_mocs.py
python3 ../_shared/generate_paper_mocs.py
```

默认配置下这个开关是开启的，所以新增的概念和论文笔记通常会自动反映到各分类目录页中。

#### Step 5: Git 提交

仅当 `GIT_COMMIT_ENABLED=true` 时执行，并且必须先检查：

1. `VAULT_PATH/.git` 存在
2. `git add -A` 后确实有 staged changes

满足条件后才 commit：

```bash
cd {VAULT_PATH} && git add -A && git commit -m "daily papers: notes YYYY-MM-DD"
```

只有在 `GIT_PUSH_ENABLED=true` 且仓库已配置远端时才 push。

### Phase 3 输出

完成后告知用户：
- 创建了多少个新概念
- 生成了多少篇论文笔记
- 回填了多少个笔记链接
- 流水线全部完成

### Phase 3 注意事项

- 如果前置文件不存在，必须先运行前面的步骤（Phase 1 / Phase 2）
- `/paper-reader` skill 会自动处理概念库补充，不要重复创建
- 仅为"必读"论文生成笔记，"值得看"不生成，耗时正常，**不是跳过的理由**
- 默认自动刷新目录页，但默认不做 git commit / push
- **绝对禁止**以下偷懒行为：
  - 自己手写 70 行骨架笔记代替 paper-reader 输出
  - 以"context overflow"为由跳过论文不生成笔记
  - 看到文件已存在就跳过，不检查质量
  - 生成笔记后不做质量验证
- 如果 context 真的接近上限：先保存已完成的笔记；只有在 `GIT_COMMIT_ENABLED=true` 时才 commit。然后**明确告知用户**还有 N 篇未完成，需要在新会话中运行 `跑一下论文笔记` 继续。绝不能默默跳过
