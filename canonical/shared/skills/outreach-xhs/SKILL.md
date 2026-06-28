---
name: outreach-xhs
description: 小红书多输入内容生成技能。用于将 pdf/md/txt/json 等文件转为结构化的小红书博文。默认生成论文解读（paper-interpretation）类型，输出 xhs-post.md 与 xhs-post.json 到输入文件所在目录，并保留可扩展模板机制以支持后续更多博文类型。
---

# XHS Post Factory

将指定文件内容转成可直接发布的小红书文案（v2 默认: 论文解读）。

## v2 工作流（两阶段）

### 阶段一：博主分析（可选，首次使用或用户要求时执行）

1. 问用户：有没有想要模仿的博主？请提供 profile 页面 URL
2. 用 opencli 拉博主帖子列表（`opencli xiaohongshu user <id>`），选 5-8 篇论文相关帖子
3. 用 Playwright `browser_run_code` 批量抓取帖子详情（正文、标签、互动数据、图片数），一次 call 跑完所有帖子
4. 保存到 `~/Desktop/Rednote/{YYYY-MM-DD}/post-details.json`
5. 生成 ~600 字分析报告 `~/Desktop/Rednote/{YYYY-MM-DD}/blogger-analysis.md`，覆盖：标题策略、标签策略、行文风格、图片配图、共性、差异
6. 问用户：分析够了吗？不够则继续加博主，够了进入阶段二

工具偏好：
- 博主列表/搜索：opencli（默认），不用 xiaohongshu MCP
- 帖子详情抓取：Playwright `browser_run_code`（批量，一次跑完）
- opencli 无法获取详情时：Playwright 或 claude-in-chrome 作为 fallback

### 阶段二：写作（用户确认分析够了才进入）

**Step 1: 生成素材库**
- 读用户提供的论文素材（pdf/md/txt/json）
- 生成素材库 md 到 `~/Desktop/Rednote/{YYYY-MM-DD}/{论文名}-xhs-draft.md`
- 素材库内容：
  - 每个板块（痛点切入、做了什么、方法亮点、关键结果、一句话总结）各写 3 个风格版本
  - 配图建议（选哪几张图、排列顺序、截图提示）
  - 5-8 个标题候选（模仿分析过的博主风格）
  - 标签推荐（广覆盖型 8-10 个）
- 板块结构可按论文内容灵活调整，不强制固定 7 段骨架
- 用户是论文作者时，语气克制不自吹

**Step 2: 用户 comment 反馈**
- 用户直接在 md 文件里写 comment（哪个版本好、怎么改、删哪段）
- 根据 comment 合并修改成单一版本

**Step 3: Humanizer 去 AI 味**
- 跑 `/humanizer` skill 做最后一轮润色
- 不改变事实内容，只调语感

**Step 4: 逐项确认（不催，等用户定了再进下一个）**
1. 文字内容 → 用户确认
2. 图片讨论（文字讨论，不生成图片）→ 用户确认
3. 标题 → 用户确认
4. 标签 → 用户确认

## Input Contract

支持输入类型:

- `pdf`
- `md`
- `txt`
- `json`

输入处理规则:

1. `pdf`
   - 优先使用同目录下已经生成的paper-card产物：`paper-card.md` + `paper-card.json`
   - 优先复用同目录下 `paper-parse` 产物: `*_content.md` + `*_parsed.json`。
   - 如果没有可复用产物，先提取可读文本，再继续生成。
2. `md` / `txt`
   - 直接作为正文语料。
3. `json`
   - 优先读取结构化字段: 标题/摘要/方法/实验/结论。
   - 字段缺失时，回退到全文字段（如 `content` / `text`）。

当输入信息不足时，明确写出"原文未明确给出"，禁止臆测补全。

## Output Contract

阶段一产物保存到 `~/Desktop/Rednote/{YYYY-MM-DD}/`：
- `post-details.json`（博主帖子详情）
- `blogger-analysis.md`（博主分析报告）

阶段二产物保存到 `~/Desktop/Rednote/{YYYY-MM-DD}/`：
- `{论文名}-xhs-draft.md`（素材库 → 迭代修改 → 最终稿）

## Template Routing

模板目录: `templates/`

路由规则:

1. 用户明确指定 `post_type` 时，优先使用指定模板。
2. 用户未指定时，按意图关键词匹配模板。
3. 默认路由到 `paper-interpretation`。
4. 模板文件不存在时，报错并提示可用模板列表。

新增模板规范:

1. 新增 `templates/<post-type>.md`。
2. 在本文件的"Template Routing"中登记触发关键词与输出要求。
3. 复用 `references/style-guide.md` 的通用风格规则。

## Paper-Interpretation 素材库骨架（v2）

素材库中每个板块写 3 个风格版本供用户选择，板块包括：

1. 痛点切入（场景代入 / 反常识 / 直给结论）
2. 这篇论文做了什么（概括展开 / 类比解释 / 技术要点）
3. 方法亮点（bullet 精简 / 对比叙事 / 数据驱动）
4. 关键结果（挑重点 / 分维度 / 浓缩版）
5. 一句话总结（3 个候选）

可选板块（按需）：
- 局限与思考
- 互动问题

附加内容（各 1 份）：
- 配图建议（选图 + 顺序 + 截图提示）
- 标题候选（5-8 个，模仿分析过的博主风格）
- 标签推荐（8-10 个，广覆盖）

## Reliability Rules

1. 不虚构事实、数字、基线、数据集。
2. 任何数值或结论都必须来自输入文件；否则删除或标注"原文未明确给出"。
3. 明确区分"作者结论"和"解读者判断"。
4. 对证据弱的结论，用保守措辞（如"可能""倾向于"）。
5. 用户是论文作者时，语气克制，不使用自吹式表达。

## Writing Style

- 标题不冗长，强调读者收益与问题意识。
- 正文短段落、清晰换行、信息块可快速扫描。
- Emoji 优先放在小标题中；正文中可适当添加增强活人感。
- 结尾使用可检索标签，但避免堆砌无关热词。
- 保持"可读性优先 + 信息可信"。
- 最终发布前跑 humanizer 去 AI 味。

## Failure Handling

遇到以下情况必须显式报错或降级说明:

- 文件不存在或格式无法读取
- 关键内容缺失导致无法形成论文解读骨架
- 模板不存在或模板未注册
- opencli / Playwright 连接失败时，提示用户检查浏览器状态

若可降级生成，正文必须包含"信息不足"提示。
