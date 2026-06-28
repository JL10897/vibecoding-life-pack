---
name: outreach-network
description: >
  Research a person's academic profile, career trajectory, and recent work,
  then compare with my research to find collaboration opportunities.
  Multi-step human-in-the-loop workflow: profile → user selects papers →
  import to Zotero/Obsidian → deep discussion.
  Use when: (1) user says "networking", "research this person", "扒一下",
  "了解一下这个人", "find collaboration points", "合作点",
  (2) user provides a researcher's name and wants to understand their work,
  (3) preparing for a meeting or email with a potential collaborator.
argument-hint: <person_name> [affiliation]
allowed-tools: [Read, Glob, Grep, Bash, Agent, WebSearch, WebFetch, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__read_page, mcp__claude-in-chrome__get_page_text, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__find, mcp__claude-in-chrome__computer, mcp__claude-in-chrome__javascript_tool]
---

> **开始前**: 先说一声 "开始学术 Networking 调研 🔍"

# Networking Expert

多步交互式工作流：了解一位学者 → 用户选论文 → 导入 Zotero → 边读边聊合作点。

**核心理念：Human-in-the-loop，边聊边做，不要一口气跑完。**

## Arguments

The user invoked this with: $ARGUMENTS

Parse: **目标姓名**（必填）+ **机构/实验室**（可选）

---

## Step 0: 向用户要信息

**不要自己去搜。** 直接问用户：

> "请给我 [Name] 的：
> 1. Google Scholar 链接
> 2. 个人主页链接（如果有的话）
>
> 有其中一个就行，两个都有更好。"

如果用户已经在调用时给了链接，跳过这步。

---

## Step 1: 读取信息源 + 生成学术画像

### 1a: 读取我的研究画像

先快速读取最新 CV，掌握自己的方向：
- `cv/en_AI/jialin_li_cv_intern_AI.tex`
- `cv/en_HCI/jialin_li_cv_intern_HCI.tex`

### 1b: 读取对方信息

用 browser tools 或 WebFetch 打开用户给的链接，提取：

**从 Google Scholar：**
- h-index、总引用
- 论文列表（尤其近 2-3 年的）
- 高被引论文

**从个人主页：**
- Bio、研究方向描述
- 教育和职位经历
- 实验室成员、项目列表
- 新闻/动态

### 1c: 输出学术画像

```markdown
# [Name] — 学术画像

**当前职位**：...
**机构**：...
**Scholar**：[link] | h-index: X
**主页**：[link]

## 人生阶段
简明的 timeline，标出每次研究方向的转变：
- [Year-Year] 在哪，做什么
- [Year-Year] 转向了什么，为什么（如果能看出来）
- [Year-至今] 现在在做什么

## 研究模块
把研究分成 3-5 个主题块，每块一句话说清楚是什么，
标注哪些是最近在活跃做的：
- **模块 A**：... （🔥 近期活跃）
- **模块 B**：... （⏸ 不太活跃）
- ...

## 近期论文（近 2-3 年）
编号列表，供挑选：
1. [2026] Title — Venue [link]
   > 一句话说这篇干了什么
2. [2025] Title — Venue [link]
   > ...
...

哪几篇看起来跟你的方向最相关我标了出来，你来挑想深入看的。
```

### ⏸ 等用户选论文

> "你想精读哪几篇？报编号就行。"

**停在这里，不要继续。**

---

## Step 2: 论文获取 + 导入 Zotero

用户选了论文后：

### 2a: 获取 PDF
- arXiv 论文：`https://arxiv.org/pdf/<id>.pdf`
- 其他来源：从论文页面找 PDF 链接
- 下载到 `/tmp/networking_papers/`

### 2b: 导入 Zotero
通过 Zotero connector API 导入（Zotero 需运行中）。确保写入 abstract。
不需要复杂的标签体系，简单导入即可。

### ⏸ 确认

> "论文已导入 Zotero。从哪篇开始聊？"

---

## Step 3: 边读边聊

这是最核心的一步。**不要搞成独白式分析报告。**

参考 `/paper-feynman` 的对话式精读方法：先获取论文全文（PDF 或网页版），
然后用交互式问答的方式逐步深入，而不是一口气输出一个总结。

### 每篇论文的起手式

先给一个简明的框架，让用户决定往哪深入：

```markdown
### [Paper Title]

**做了什么**：一两句话
**方法**：核心技术路线
**跟你的关联**：
- [具体说哪个项目/方向能接上]
- [他有什么你没有的，你有什么他可能需要的]

**想跟你讨论的点**：
- [一个具体的技术问题或合作可能性]
```

然后**等用户反应**。用户可能：
- 追问细节 → 回到原文找到对应段落，精确回答
- 说"下一篇" → 换论文
- 提出自己的想法 → 接着聊
- 说"总结一下" → 进入 Step 4

**关键：合作点是聊出来的，不是算出来的。**
在讨论中自然地抛出可能的合作方向，而不是最后列一个大表。
目标是 inspire 用户，不是给用户一份报告。

---

## Step 4: 生成 Obsidian Networking 笔记（Deliverable）

讨论告一段落后（用户说"总结一下"、"存一下"、或自然结束时），
生成一份 Networking 笔记保存到 Obsidian。

### 路径与命名

读取 `_shared/user-config.json` 获取 `VAULT_PATH`。

保存到：`{VAULT_PATH}/Networking/[Name]_[YYYY-MM-DD].md`

如果 `Networking/` 文件夹不存在，创建它。

### 笔记模板

```markdown
---
title: "Networking：[Name]"
date: [YYYY-MM-DD]
person: "[Name]"
affiliation: "[Affiliation]"
scholar: "[Google Scholar URL]"
homepage: "[Homepage URL]"
tags: [networking]
---

# [Name]

## 基本信息
- **当前职位**：...
- **机构**：...
- **Scholar**：[link] | h-index: X
- **主页**：[link]

## 人生阶段
[从 Step 1 的画像中搬过来，保持简明 timeline 格式]

## 研究模块
[从 Step 1 搬过来]

## 精读论文
[对每篇在 Step 3 中讨论过的论文，记录：]

### [Paper 1 Title]
- **链接**：...
- **核心内容**：2-3 句话
- **跟我的关联**：[讨论中聊出来的具体关联点]

### [Paper 2 Title]
...

## 合作灵感
[把讨论过程中自然产生的合作想法整理在这里，不需要格式化模板，
用自然语言记录核心 idea 即可]

## 下一步
- [ ] ...
- [ ] ...

## 讨论备忘
[如果讨论中有值得记下来的 insight、用户的判断、或者未展开的线索，
简要记在这里，方便下次回看]
```

### 写入后告知用户

> "Networking 笔记已保存到 Obsidian：`Networking/[Name]_[date].md`"

---

## 原则

1. **每步等用户** — 不自动推进
2. **语言跟用户走** — 用户用中文你就用中文
3. **不编造** — 找不到就说找不到
4. **同名消歧** — 常见名字要确认
5. **关联要具体** — 说"他的 X 方法可以用在你的 Y 数据上"，不说"都做 AI"
6. **轻量** — 不要过度结构化，聊天感 > 报告感
