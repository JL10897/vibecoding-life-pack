---
name: research-idea-refine
description: "Iteratively refine research problem decomposition and method via Claude + GPT-5.4 peer review loop. Use when user says \"refine my approach\", \"帮我细化方案\", \"decompose this problem\", \"打磨idea\", \"refine research plan\", \"细化研究方案\", or wants to turn a vague research idea into a concrete, top-venue-ready plan."
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, AskUserQuestion, mcp__codex__codex, mcp__codex__codex-reply
---

# Research Refine: Iterative Problem Decomposition & Method Concretization

Refine and concretize: **$ARGUMENTS**

## Overview

Given a research PROBLEM and a vague APPROACH, iteratively refine the problem decomposition and method into a concrete, top-venue-ready plan through a Claude + GPT-5.4 peer review loop. This skill fills the gap between "I have a vague idea" and "let me implement it."

```
User input (PROBLEM + vague APPROACH)
  → 🧑 Phase 0: Ask user about target venue → determine VENUE_TYPE (ML or HCI)
  → Phase 1 (Claude): Scan local papers → Decompose problem → Concretize method → Write initial proposal (template varies by VENUE_TYPE)
  → 🧑 Checkpoint A: User reviews initial proposal → confirm / edit / redirect
  → Phase 2 (Codex/GPT-5.4): 6-dimension peer review + scoring (1-10)
  → 🧑 Checkpoint B: User triages reviewer feedback → accept / reject / discuss each point
  → Phase 3 (Claude): Revise proposal based on user-approved changes → Track changes
  → 🧑 Checkpoint C: User reviews revised proposal → confirm sending to reviewer / request edits
  → Phase 4 (Codex, same thread): Re-evaluate revised proposal
  → Repeat Checkpoint B → Phase 3 → Checkpoint C → Phase 4 until OVERALL SCORE >= 7 or MAX_ROUNDS (5) reached
  → Phase 5: Save all iteration history to refine-logs/
```

> 🧑 = Human-in-the-loop checkpoint. The loop is conversational — Claude presents information, asks focused questions, and the user guides decisions. The user can always say "looks good, go ahead" to move fast, or dive deep into any point.

## Constants

- **REVIEWER_MODEL = `gpt-5.4`** — Model used via Codex MCP for peer review. Must be an OpenAI model (e.g., `gpt-5.4`, `o3`, `gpt-4o`).
- **MAX_ROUNDS = 5** — Maximum number of review-revise rounds before forced termination.
- **SCORE_THRESHOLD = 7** — Minimum overall score to stop iterating. A plan rated 6/10 isn't worth implementing.
- **OUTPUT_DIR = `refine-logs/`** — Directory for per-round files and final report.
- **MAX_LOCAL_PAPERS = 15** — Maximum number of local papers to scan for grounding.

> 💡 Override via argument, e.g., `/research-idea-refine "problem | approach" — max rounds: 3, threshold: 8`.

## Output Structure

```
refine-logs/
├── round-0-initial-proposal.md
├── round-1-review.md
├── round-1-refinement.md
├── round-2-review.md
├── round-2-refinement.md
├── ...
├── REFINEMENT_REPORT.md        (final summary + all raw responses)
├── PROPOSAL.md                 (formal proposal with citation list, English)
├── PROPOSAL_ZH.md              (formal proposal with citation list, 中文)
└── score-history.md            (score evolution table)
```

## Workflow

### 🧑 Phase 0: Venue & Direction Alignment

Before doing ANY research or writing, have a brief conversation with the user to understand the target venue and contribution type. This determines the entire downstream workflow.

**Ask the user:**

```
开始之前先确认一下方向——你这个工作打算投哪个 venue？

比如：
- AI/ML 系：NeurIPS, ICLR, ICML, AAAI, ...
- HCI/多媒体系：CHI, ACM MM, UIST, CSCW, ...
- 还没确定的话也没关系，你大概描述一下工作的性质我来帮你判断。
```

**Determine VENUE_TYPE based on user's response:**

- **`ML`** — Target is NeurIPS, ICLR, ICML, AAAI, or similar. Core contribution is algorithmic/model/theoretical.
- **`HCI`** — Target is CHI, ACM MM, UIST, CSCW, DIS, or similar. Core contribution involves user study, interaction design, system+evaluation, or human factors.

If the user names a specific venue, set `TARGET_VENUE` (e.g., "CHI 2026") for use in reviewer prompts.

If the work is cross-disciplinary (e.g., an AI system evaluated with user studies for CHI), ask:

```
这个工作感觉有点交叉——核心贡献更偏技术（新模型/算法），还是更偏用户侧（交互设计/用户研究）？这会影响我写 proposal 和选 reviewer 视角的方式。
```

**Save VENUE_TYPE** as a variable used throughout the rest of the workflow. All subsequent phases branch on this.

---

### Phase 1: Problem Decomposition & Initial Proposal

Build a grounded, concrete initial proposal from the user's vague input. **The structure and emphasis differ based on VENUE_TYPE.**

#### Step 1.1: Scan Local Paper Library

Check `papers/` and `literature/` in the project directory for existing PDFs and notes. Read first 3 pages of relevant papers (up to MAX_LOCAL_PAPERS) to build a baseline understanding.

- Identify relevant methods, baselines, evaluation protocols
- Note recurring experimental setups and metrics in the area
- Extract key assumptions and limitations from related work
- Build a list of "grounding references" to cite in the proposal

Also search online if local papers are insufficient:
- Use WebSearch for recent arXiv preprints and top venue papers
- Focus on methodological details (not just abstracts)

#### Step 1.2: Decompose the Problem

Break the user's problem into concrete sub-problems. The decomposition emphasis differs by venue type:

**If VENUE_TYPE = ML:**

1. **Core research question**: What technical problem are we solving?
2. **Sub-questions**: What smaller technical questions must be answered first?
3. **Assumptions**: What must be true for this approach to work?
4. **Key technical challenges**: What are the hardest algorithmic/modeling parts?
5. **Evaluation criteria**: Which benchmarks and metrics prove the method works?

**If VENUE_TYPE = HCI:**

1. **Core research question**: What user need / interaction problem are we addressing?
2. **Target users**: Who are we designing for? What is their context?
3. **Design goals**: What properties should the solution have from a user perspective?
4. **Sub-questions**: What do we need to understand about user behavior / needs first?
5. **Key challenges**: What are the hardest design / engineering / study design parts?
6. **Contribution type**: Empirical (user study findings), Artifact (system/tool), Methodological (new method for studying X), or a combination?
7. **Evaluation approach**: How will we know the design works? (User study? Deployment? Mixed methods?)

#### Step 1.3: Concretize the Method

Transform the vague approach into a specific plan. The structure differs significantly by venue type.

**If VENUE_TYPE = ML:**

1. **Algorithm / pipeline**: Step-by-step description of the proposed method
2. **Key design choices**: Why this architecture / loss / training procedure?
3. **Baselines**: What are we comparing against? (minimum 2-3 strong baselines)
4. **Datasets**: Which datasets, what splits, what preprocessing?
5. **Metrics**: Primary and secondary evaluation metrics
6. **Ablations**: What components to ablate to prove each design choice matters?
7. **Expected results**: What do we expect to see, and why? (be specific about magnitudes)

**If VENUE_TYPE = HCI:**

1. **System / interaction design**: What does the system do? What is the interaction flow? Key design rationale?
2. **Design process**: How did we arrive at this design? (formative study, iterative prototyping, design workshops, etc.)
3. **Implementation**: Key technical components (but focus on what enables the user experience, not algorithmic novelty for its own sake)
4. **Study design**:
   - Study type: Lab study / field deployment / online experiment / wizard-of-oz / etc.
   - Participants: Target N, recruitment strategy, inclusion criteria, demographics
   - Tasks: What participants will do, why these tasks are representative
   - Conditions: Within/between-subjects, control condition
   - Measures: Quantitative (task completion, time, SUS, NASA-TLX, custom scales) + Qualitative (interviews, think-aloud, thematic analysis)
   - Procedure: Step-by-step protocol
5. **IRB / Ethics**: Any ethical considerations, consent process
6. **Comparison systems**: What existing tools/systems are we comparing against? (not just algorithmic baselines — think competing UX approaches)
7. **Expected findings**: What patterns do we expect in user behavior? What themes might emerge from qualitative data?

#### Step 1.4: Write Initial Proposal

Compile everything into a structured proposal document. **Use the template matching VENUE_TYPE.**

**If VENUE_TYPE = ML:**

```markdown
# Research Proposal: [Title]

## Problem Statement
[Clear, specific problem definition]

## Research Questions
1. [Primary RQ]
2. [Sub-RQ 1]
3. [Sub-RQ 2]

## Proposed Method
### Overview
[1-paragraph summary]

### Detailed Method
[Step-by-step algorithm/pipeline description]

### Key Design Choices
[Justified decisions with references to local papers]

## Experimental Design
### Baselines
- [Baseline 1]: [why it's relevant]
- [Baseline 2]: [why it's relevant]
- [Baseline 3]: [why it's relevant]

### Datasets
- [Dataset 1]: [size, split, preprocessing]
- [Dataset 2]: [size, split, preprocessing]

### Evaluation Metrics
- Primary: [metric + justification]
- Secondary: [metrics]

### Ablation Studies
1. [Component 1]: remove/replace to test [hypothesis]
2. [Component 2]: remove/replace to test [hypothesis]

## Expected Results
[What we expect and why — be specific about magnitudes]

## Assumptions & Risks
- [Assumption 1]: [what happens if wrong]
- [Risk 1]: [mitigation strategy]

## Compute & Timeline Estimate
- Estimated GPU-hours: [X]
- Timeline: [X days/weeks]
```

**If VENUE_TYPE = HCI:**

```markdown
# Research Proposal: [Title]

## Motivation & Problem
[What user need or interaction challenge are we addressing? Why does it matter? Who is affected?]

## Research Questions
1. [Primary RQ — framed around users/interaction, not algorithms]
2. [Sub-RQ 1]
3. [Sub-RQ 2]

## Contribution Type
[Empirical / Artifact / Methodological / Mixed — and why this framing]

## Related Work & Design Space
### Prior Systems
[Existing tools/systems that address similar needs — what works, what doesn't]

### Theoretical Grounding
[Relevant theories from HCI, psychology, cognitive science, etc. that inform the design]

## System Design
### Design Rationale
[Why this design? What user needs drove each key decision? Reference formative findings if applicable]

### Interaction Flow
[Step-by-step user interaction walkthrough]

### Key Design Decisions
[Decision 1]: [alternatives considered, why this choice]
[Decision 2]: [alternatives considered, why this choice]

### Implementation
[Technical architecture — focus on what enables the user experience]

## Study Design
### Study Type
[Lab study / field deployment / online experiment / longitudinal / ...]

### Participants
- Target N: [X] (power analysis or precedent justification)
- Recruitment: [strategy]
- Inclusion criteria: [who qualifies]

### Conditions
[Within/between-subjects, what conditions, control/baseline system]

### Tasks
[What participants will do — must be representative of real use]

### Measures
#### Quantitative
- [Task performance: completion rate, time, error rate]
- [Subjective: SUS, NASA-TLX, Likert scales, custom instruments]

#### Qualitative
- [Think-aloud / semi-structured interview / open-ended survey]
- [Analysis method: thematic analysis / affinity diagramming / ...]

### Procedure
[Step-by-step protocol: consent → intro → training → tasks → questionnaire → interview → debrief]

### IRB & Ethics
[Status, key ethical considerations, consent process, data handling]

## Comparison Systems
- [System 1]: [what it represents in the design space]
- [System 2]: [what it represents]

## Expected Findings
### Quantitative Hypotheses
- H1: [e.g., "Our system will reduce task completion time by X% compared to baseline"]
- H2: [...]

### Qualitative Expectations
[What themes might emerge? What aspects of user experience are we most interested in understanding?]

## Assumptions & Risks
- [Recruitment risk]: [mitigation]
- [Ecological validity concern]: [mitigation]
- [Technical risk]: [mitigation]

## Timeline
- Design & implementation: [X weeks]
- Pilot study: [X weeks]
- Main study: [X weeks]
- Analysis & writing: [X weeks]
```

Save this proposal to `refine-logs/round-0-initial-proposal.md`.

### 🧑 Checkpoint A: User Reviews Initial Proposal

Before sending anything to the reviewer, present the proposal to the user in a conversational way. Do NOT just dump the full document — instead, give a structured summary and ask for input.

**Present to the user:**

```
我已经根据你的想法和相关文献写了一个初步的 proposal，主要包括：

**核心研究问题**: [1-2 sentences]
**提出的方法**: [1-2 sentences — the key idea]
**主要创新点**: [what makes this different from existing work]
**实验方案**: [datasets] + [baselines] + [metrics]

完整 proposal 已保存到 refine-logs/round-0-initial-proposal.md

在发给 reviewer 之前，想先跟你确认几个点：
1. 研究问题的 framing 你觉得准确吗？还是你想强调的方向有所不同？
2. 方法的核心思路对吗？有没有你觉得重要但我漏掉的设计选择？
3. 实验设计有没有你特别想加的 baseline 或 dataset？

你可以说 "没问题，发吧" 直接进入 review，也可以说具体想改什么。
```

**User response handling:**
- **"没问题" / "go ahead" / "发吧"** → Proceed to Phase 2 immediately
- **User gives specific feedback** → Incorporate changes into the proposal, update `round-0-initial-proposal.md`, then re-present the changed parts for confirmation. Do NOT re-show the entire proposal — only show what changed and why.
- **User wants to discuss** → Have a natural conversation. Answer questions, explain reasoning, explore alternatives. Once alignment is reached, update the proposal and proceed.

**Tone**: Be a collaborator, not a report generator. Think of this as a whiteboard session with a co-author.

### Phase 2: External Peer Review (Round 1)

Send the full proposal to GPT-5.4 for a rigorous 6-dimension review:

```
mcp__codex__codex:
  model: REVIEWER_MODEL
  config: {"model_reasoning_effort": "xhigh"}
  prompt: |
    You are a senior ML reviewer for a top venue (NeurIPS/ICML/ICLR).
    Below is a research proposal. Please provide a rigorous peer review.

    === PROPOSAL ===
    [Paste the FULL proposal from Phase 1]
    === END PROPOSAL ===

    Score each dimension 1-10 and provide specific, actionable feedback:

    1. **Clarity** (1-10): Is the problem well-defined? Is the method description precise enough to reproduce? Are the research questions specific and answerable?

    2. **Novelty** (1-10): Does this propose something genuinely new, or is it incremental? How does it differentiate from the closest existing work? Would a reviewer say "so what?"

    3. **Feasibility** (1-10): Can this actually be implemented and run with reasonable resources? Are the compute estimates realistic? Are the datasets accessible?

    4. **Experimental Design** (1-10): Are the baselines strong and fair? Are the metrics appropriate? Are the ablations sufficient to isolate contributions? Is the evaluation rigorous?

    5. **Venue Fit** (1-10): Would this be competitive at a top venue? Is the contribution substantial enough? Does the framing match what reviewers expect?

    6. **Completeness** (1-10): Are there missing baselines, datasets, or analyses? Are there obvious experiments that should be included? Any gaps in the logical chain?

    **OVERALL SCORE** (1-10): Weighted average reflecting your holistic assessment.

    For each dimension scoring < 7, provide:
    - The specific weakness
    - A concrete, actionable suggestion to fix it
    - Priority: CRITICAL (must fix) / IMPORTANT (should fix) / MINOR (nice to fix)

    Finally, give a VERDICT: READY (score >= 7, plan is implementable) / REVISE (specific fixes needed) / RETHINK (fundamental issues with approach)
```

**CRITICAL: Save the threadId** from this call for all subsequent rounds.

**CRITICAL: Save the FULL raw response** verbatim — do NOT discard or summarize.

Save the review to `refine-logs/round-1-review.md` with the raw response in a `<details>` block.

### Phase 3: Parse Feedback & Revise Proposal

#### Step 3.1: Parse Review

Extract structured fields from the reviewer's response (internally — do NOT dump the raw review to the user):

- **Per-dimension scores**: Clarity, Novelty, Feasibility, Exp Design, Venue Fit, Completeness
- **Overall score** (1-10)
- **Verdict**: READY / REVISE / RETHINK
- **Action items**: Ranked list with priority (CRITICAL / IMPORTANT / MINOR)

Update `refine-logs/score-history.md`:

```markdown
# Score Evolution

| Round | Clarity | Novelty | Feasibility | Exp Design | Venue Fit | Completeness | Overall | Verdict |
|-------|---------|---------|-------------|------------|-----------|--------------|---------|---------|
| 1     | X       | X       | X           | X          | X         | X            | X       | REVISE  |
```

**STOP CONDITION**: If overall score >= SCORE_THRESHOLD AND verdict is READY → skip to Phase 5.

### 🧑 Checkpoint B: Walk Through Reviewer Feedback One-by-One

Present the reviewer's feedback **one item at a time** in a natural conversation. Do NOT list all feedback at once — discuss each point, get the user's decision, then move to the next.

#### Step B.1: Open with a Score Overview

Start with a brief overview so the user has context, then immediately move to the first item:

```
Reviewer 给了 X/10 分 (verdict: [VERDICT])。
  Clarity [X] | Novelty [X] | Feasibility [X] | Exp Design [X] | Venue Fit [X] | Completeness [X]

一共有 N 个修改建议，我们一个一个来看。先说最重要的：

🔴 第 1 点 (CRITICAL)：
Reviewer 觉得 [用自然语言概括，2-3 句话]。

我的看法：[Claude 的判断 — 同意/不同意/部分同意，1-2 句话说明理由]。
我建议 [具体的修改方案 / 或者建议 push back 的理由]。

你觉得呢？
```

#### Step B.2: Process Each Item Sequentially

After the user responds to one item, present the next:

```
好的，第 1 点 [记录决定]。

接下来第 2 点 🔴 (CRITICAL)：
[同样的格式：reviewer 说了什么 → 我的看法 → 建议]

你怎么看？
```

**Conversation style:**
- **One item per message.** Wait for user response before showing the next item.
- **Translate, don't parrot.** Summarize in plain language — the user shouldn't have to parse academic review jargon.
- **Present YOUR opinion first.** Give the user a concrete position to react to. "我觉得这个说得对，因为..." or "这个我不太同意，因为..." is much easier to respond to than "你觉得呢？"
- **Keep it natural.** This should feel like two co-authors chatting about feedback, not a form to fill out.
- **Support terse responses.** "改" / "不改" / "同意" / "你说的对" / "随你" are all valid responses. Don't ask for elaboration unless the point is genuinely ambiguous.

**User response handling per item:**
- **"改" / "同意" / "ok"** → Record as ✅ Accept, move to next item
- **"不改" / "push back"** → Ask briefly for their reasoning (one sentence is fine), record as ❌ Reject, move to next
- **User proposes alternative** → Discuss briefly, record as 🔄 Alternative, move to next
- **"随你"** → Record as 🤖 Defer (Claude decides), move to next
- **User wants to discuss deeper** → Engage in focused back-and-forth on THIS point until resolved, then move to next

#### Step B.3: Batch Shortcut

If at any point the user says something like "剩下的都改" / "剩下随你" / "后面的 minor 的你看着办", accept the batch decision and skip the remaining individual discussions. Don't force the user to go through every single MINOR point if they don't want to.

#### Step B.4: Confirm Summary

After all items are discussed, present a quick summary:

```
好，这轮 reviewer 的意见我们都过了一遍：
  ✅ 改：第 1、3 点
  ❌ 不改：第 2 点（因为 [user's reason]）
  🔄 替代方案：第 4 点
  🤖 我来定：第 5 点

我去改 proposal 了。
```

Wait for a final "好" / "ok" before proceeding to Step 3.2. If the user has second thoughts, adjust.

Record all decisions in `refine-logs/round-N-refinement.md` under a `## User Decisions` section.

#### Step 3.2: Revise Proposal (Based on User-Approved Changes)

For each action item, follow the user's decision from Checkpoint B:

1. **User said "改" (accept)**: Implement the fix in the proposal
2. **User said "push back"**: Add a "Pushback" note with the user's reasoning (and supporting evidence from local papers if applicable). Do NOT implement the change.
3. **User gave alternative**: Implement the user's version instead of the reviewer's suggestion
4. **User said "随你" (defer to Claude)**: Use your own judgment — assess against local papers, implement or pushback accordingly

**Track all changes**: For each revision, note:
- What was changed
- The user's decision and reasoning
- What evidence supports the change (or pushback)

**Rewrite the full proposal**: Produce a complete updated proposal (not a diff — GPT needs the full text in context).

Save to `refine-logs/round-N-refinement.md`:

```markdown
# Round N Refinement

## User Decisions

| # | Reviewer Feedback | User Decision | Reasoning |
|---|-------------------|---------------|-----------|
| 1 | [summary] | ✅ Accept | [user's reasoning or "defer to Claude"] |
| 2 | [summary] | ❌ Reject | [user's reasoning] |
| 3 | [summary] | 🔄 Alternative | [user's alternative approach] |
| 4 | [summary] | 🤖 Defer | [Claude's judgment + reasoning] |

## Changes Made

### 1. [Section changed]
- **Reviewer said**: [quote]
- **User decided**: [accept / reject / alternative]
- **Action**: [what was changed]
- **Reasoning**: [why, with evidence]

### 2. [Section changed]
- **Reviewer said**: [quote]
- **User decided**: [pushback]
- **Action**: [kept original with justification]
- **Evidence**: [citation from local papers or user's reasoning]

...

## Revised Proposal

[Full updated proposal text]
```

### 🧑 Checkpoint C: User Reviews Revised Proposal Before Re-submission

After completing the revision, present a quick diff summary before sending back to the reviewer.

**Present to the user:**

```
这轮改完了，主要改了这些：

1. ✅ [改动 1 的一句话总结]
2. ❌ [Push back 的点 + 理由简述]
3. 🔄 [用了你的替代方案: ...]

修改后的 proposal 已保存到 refine-logs/round-N-refinement.md

要发给 reviewer 做下一轮 review 吗？还是你想再调整什么？
```

**User response handling:**
- **"发吧" / "go"** → Proceed to Phase 4
- **User wants more changes** → Apply changes, update the file, re-present the diff
- **"够了，不用再 review 了"** → Skip to Phase 5 (final report) with current state
- **"我想加一个新的点..."** → Incorporate, update file, then re-present

### Phase 4: Re-evaluation (Round 2+)

Send the revised proposal back to GPT-5.4 using the **same thread** for continuity:

```
mcp__codex__codex-reply:
  threadId: [saved from Phase 2]
  model: REVIEWER_MODEL
  config: {"model_reasoning_effort": "xhigh"}
  prompt: |
    [Round N re-evaluation]

    I have revised the proposal based on your feedback. Here are the key changes:

    1. [Change 1]: [brief description + reasoning]
    2. [Change 2]: [brief description + reasoning]
    3. [Pushback on point X]: [your evidence for disagreeing]

    === REVISED PROPOSAL ===
    [Paste the FULL revised proposal — you cannot read files]
    === END REVISED PROPOSAL ===

    Please re-score all 6 dimensions and overall. For each dimension:
    - Has the score improved, stayed the same, or decreased?
    - If the author pushed back on your feedback, do you accept their reasoning?
    - Are there NEW issues introduced by the revisions?

    Same format: 6 dimension scores, overall score, verdict, remaining action items with priorities.
```

Save review to `refine-logs/round-N-review.md`.

**Then return to Phase 3** (parse → Checkpoint B → revise → Checkpoint C → re-evaluate) until:
- **Overall score >= SCORE_THRESHOLD** AND verdict is READY → proceed to Phase 5
- **MAX_ROUNDS reached** → proceed to Phase 5 with current state
- **User says "够了"** at any Checkpoint → proceed to Phase 5 with current state

### Phase 5: Final Report & Logs

#### Step 5.1: Write REFINEMENT_REPORT.md

Save to `refine-logs/REFINEMENT_REPORT.md`:

```markdown
# Refinement Report

**Problem**: [user's problem]
**Initial Approach**: [user's vague approach]
**Date**: [today]
**Rounds**: N / MAX_ROUNDS
**Final Score**: X / 10
**Final Verdict**: [READY / REVISE / RETHINK]

## Score Evolution

| Round | Clarity | Novelty | Feasibility | Exp Design | Venue Fit | Completeness | Overall | Verdict |
|-------|---------|---------|-------------|------------|-----------|--------------|---------|---------|
| 1     | ...     | ...     | ...         | ...        | ...       | ...          | ...     | ...     |
| 2     | ...     | ...     | ...         | ...        | ...       | ...          | ...     | ...     |
| ...   | ...     | ...     | ...         | ...        | ...       | ...          | ...     | ...     |

## Final Proposal

[Full text of the final refined proposal]

## Key Refinements Made

1. [Most impactful change + reasoning]
2. [Second most impactful change + reasoning]
3. ...

## Pushback Log

| Round | Reviewer Said | Author Response | Outcome |
|-------|---------------|-----------------|---------|
| 1     | [criticism]   | [pushback + evidence] | [accepted/rejected by reviewer] |
| ...   | ...           | ...             | ...     |

## Remaining Weaknesses

[Issues not fully resolved — honest assessment]

## Raw Reviewer Responses

<details>
<summary>Round 1 Review</summary>

[Full verbatim response from GPT-5.4]

</details>

<details>
<summary>Round 2 Review</summary>

[Full verbatim response from GPT-5.4]

</details>

...

## Next Steps

- If READY: proceed to implementation → `/run-experiment` → `/auto-review-loop`
- If REVISE: address remaining weaknesses manually, then re-run `/research-idea-refine`
- If RETHINK: reconsider the fundamental approach, possibly re-run `/idea-creator`
```

#### Step 5.2: Write Formal Proposal (PROPOSAL.md)

Compile the final refined plan into a clean, self-contained proposal document. This is the deliverable the user can share with collaborators or use as a blueprint for writing the actual paper.

Gather all references cited throughout the refinement process — from local paper scans (Phase 1), web searches, and reviewer suggestions — and compile them into a structured citation list at the end.

Save to `refine-logs/PROPOSAL.md`:

```markdown
# [Proposal Title]

## 1. Problem Statement

[Clear definition of the problem. What is the task? Why does it matter? What is the real-world or scientific motivation?]

## 2. Research Gap

[What is missing in current work? Why are existing methods insufficient? What specific gap does this proposal address? Cite relevant prior work to substantiate the gap.]

## 3. Literature Review

[Structured review of the most relevant prior work. Group by theme or methodology. For each work, briefly describe its contribution and its limitation that motivates your approach. Cite using [N] notation.]

## 4. Proposed Method

[Full description of the proposed approach — architecture, algorithm, pipeline, training procedure, key design choices with justifications.]

## 5. Experimental Design

### 5.1 Datasets
- [Dataset 1]: [description, size, splits, preprocessing]
- [Dataset 2]: [description, size, splits, preprocessing]

### 5.2 Baselines
- [Baseline 1]: [why selected, expected comparison]
- [Baseline 2]: [why selected, expected comparison]
- [Baseline 3]: [why selected, expected comparison]

### 5.3 Evaluation Metrics
- Primary: [metric + justification]
- Secondary: [metrics]

### 5.4 Ablation Studies
1. [Ablation 1]: [what it tests]
2. [Ablation 2]: [what it tests]

### 5.5 Compute & Timeline
- Estimated GPU-hours: [X]
- Timeline: [X days/weeks]

## 6. Questions to Be Discussed

[Open questions, uncertainties, and decision points that need further discussion with collaborators or advisors. These might include alternative design choices, scope decisions, or potential pivots.]

1. [Question 1 — e.g., "Should we use X or Y as the backbone? Trade-off is ..."]
2. [Question 2 — e.g., "Is dataset Z large enough, or do we need to augment?"]
3. [Question 3]

## References

| # | Title | Authors | Venue | Year | Link |
|---|-------|---------|-------|------|------|
| 1 | [Paper title] | [First Author et al.] | [e.g., NeurIPS 2025] | [Year] | [URL or arXiv link] |
| 2 | [Paper title] | [First Author et al.] | [e.g., ACL 2024] | [Year] | [URL or arXiv link] |
| ... | ... | ... | ... | ... | ... |
```

**Rules for the References table:**
- Include ALL papers cited anywhere in the proposal (literature review, method justification, baseline descriptions, etc.)
- Each entry must have: title, authors, venue (conference/journal name), year, and a link (arXiv, DOI, or Semantic Scholar URL)
- If a paper was found via local library scan, use the metadata from the PDF. If found via web search, include the URL from the search result.
- Order by first appearance in the proposal text (matching [N] citations)
- Do NOT include papers that are not actually cited in the proposal body

#### Step 5.2b: Write Chinese Proposal (PROPOSAL_ZH.md)

Translate the English PROPOSAL.md into a Chinese version. This is NOT a mechanical translation — adapt the writing style to be natural academic Chinese (学术中文).

Save to `refine-logs/PROPOSAL_ZH.md`:

```markdown
# [提案标题]

## 1. 问题陈述

[清晰定义研究问题。任务是什么？为什么重要？现实世界或科学层面的动机是什么？]

## 2. 研究空白

[当前工作中缺少什么？为什么现有方法不够？本提案具体填补了哪个空白？引用相关先前工作来支撑论述。]

## 3. 文献综述

[结构化综述最相关的先前工作。按主题或方法论分组。对于每项工作，简要描述其贡献及其局限性，说明为何需要本文的方法。使用 [N] 标注引用。]

## 4. 提出的方法

[完整描述提出的方法——架构、算法、流程、训练过程、关键设计选择及其理由。]

## 5. 实验设计

### 5.1 数据集
- [数据集 1]：[描述、规模、划分、预处理]
- [数据集 2]：[描述、规模、划分、预处理]

### 5.2 基线方法
- [基线 1]：[选择原因、预期对比]
- [基线 2]：[选择原因、预期对比]
- [基线 3]：[选择原因、预期对比]

### 5.3 评估指标
- 主要指标：[指标 + 理由]
- 次要指标：[指标]

### 5.4 消融实验
1. [消融 1]：[验证什么]
2. [消融 2]：[验证什么]

### 5.5 计算资源与时间线
- 预计 GPU 小时数：[X]
- 时间线：[X 天/周]

## 6. 待讨论问题

[需要与合作者或导师进一步讨论的开放性问题、不确定性和决策点。]

1. [问题 1]
2. [问题 2]
3. [问题 3]

## 参考文献

| # | 标题 | 作者 | 发表venue | 年份 | 链接 |
|---|------|------|----------|------|------|
| 1 | [论文标题] | [第一作者 等] | [如 NeurIPS 2025] | [年份] | [URL] |
| 2 | [论文标题] | [第一作者 等] | [如 ACL 2024] | [年份] | [URL] |
| ... | ... | ... | ... | ... | ... |
```

**Rules:**
- The content must be substantively identical to PROPOSAL.md — same references, same experimental design, same method details.
- Use natural academic Chinese, not machine-translated text. Technical terms can keep their English form where standard (e.g., Transformer, attention, ablation).
- The References table should be identical to the English version (paper titles stay in English in the table).

#### Step 5.3: Finalize score-history.md

Ensure `refine-logs/score-history.md` contains the complete score evolution table.

#### Step 5.4: Present Summary to User

```
📋 Refinement complete after N rounds.

Final score: X/10 (Verdict: READY/REVISE/RETHINK)

Score evolution:
  Round 1: X/10 → Round 2: Y/10 → ... → Round N: Z/10

Key improvements:
- [biggest change 1]
- [biggest change 2]

Remaining concerns:
- [if any]

Full report: refine-logs/REFINEMENT_REPORT.md
Formal proposal (EN): refine-logs/PROPOSAL.md
Formal proposal (中文): refine-logs/PROPOSAL_ZH.md
Final refinement: refine-logs/round-N-refinement.md
```

#### Step 5.5: 🧑 Collaboration Retrospective

After presenting the summary, ask the user for feedback on the collaboration process itself:

```
最后想问一下，这次合作的过程你觉得怎么样？

比如：
- 我问你意见的频率合适吗？（太多/太少/刚好）
- 讨论 reviewer 反馈的方式好用吗？
- 有没有哪个环节你觉得可以改进的？

如果有什么想调整的，我可以直接帮你改 skill 的设置，下次就按新的方式来。
```

**If the user gives feedback:**
- Acknowledge the feedback
- If actionable (e.g., "问少一点" / "不用每次都确认" / "reviewer 的意见可以一起列出来"), offer to modify the SKILL.md accordingly. Explain what you would change and ask for confirmation before editing.
- Save significant process preferences to memory (via the memory system) so they persist across conversations.

**If the user says "挺好的" / no feedback:**
- Thank them and wrap up. Do not push for more feedback.

## Key Rules

- **Human-in-the-loop is non-negotiable.** NEVER skip Checkpoints A, B, or C. The user must have the opportunity to review, approve, or redirect at every checkpoint. However, make checkpoints lightweight — the user should be able to pass through with a single word ("go", "发吧", "ok") when they're satisfied. The goal is conversational co-authoring, not bureaucratic approval gates.
- **Be a co-author, not a secretary.** At each checkpoint, present YOUR opinion on the reviewer's feedback. Don't just relay what the reviewer said — tell the user what you think about it and why. This gives the user something concrete to react to, which is much faster than open-ended questions.
- **One item at a time in Checkpoint B.** Do NOT list all reviewer feedback at once. Walk through each point individually — present it, give your opinion, wait for the user's response, then move to the next. This is a conversation, not a checklist.
- **Support shorthand.** "改" / "不改" / "随你" are complete responses. Accept Chinese/English mixed input. If the user says "剩下的都随你", batch-process the rest without asking one-by-one.
- **ALWAYS use `config: {"model_reasoning_effort": "xhigh"}`** for all Codex calls — maximum reasoning depth for plan-level review.
- **Save threadId from Phase 2**, use `mcp__codex__codex-reply` for all subsequent rounds (Phase 4). Do NOT create a new thread per round.
- **Full proposal re-sent every round** — GPT cannot read files. Always paste the complete revised proposal in the prompt, not just a diff.
- **Pushback is encouraged.** Do NOT blindly accept all reviewer feedback. Use local paper evidence to disagree when the reviewer is wrong. This makes the loop more robust than one-directional compliance.
- **Per-round files, not a single log.** Save each review and refinement as a separate file in `refine-logs/` for easy diffing and tracking.
- **Threshold 7, not 6.** A plan rated 6/10 isn't worth implementing — the bar must be higher than for a finished paper review because the plan still needs to survive implementation and full review.
- **Do NOT fabricate results.** The proposal should describe *expected* results and *planned* experiments, not claim results that don't exist yet.
- **Be specific about compute.** Vague "we'll train a model" is not a plan. Specify GPU-hours, dataset sizes, training iterations.
- **Baselines are non-negotiable.** Every proposal must include at least 2-3 strong, relevant baselines. "We compare against random" is not acceptable.
- **Document everything.** Every round's raw review, every change made, every pushback. The refinement log should be a complete record of the plan's evolution.

## Composing with Other Skills

This skill sits between idea discovery and implementation in the research pipeline:

```
/idea-creator "direction"       → ranked ideas with pilot results
/research-idea-refine "PROBLEM: ... | APPROACH: ..."  ← you are here
/run-experiment                 → deploy full-scale experiments
/auto-review-loop               → iterate on results until submission-ready
```

**Typical flow:**
1. `/idea-creator` produces a top idea with a positive pilot signal
2. `/research-idea-refine` takes that idea and turns the vague plan into a concrete, reviewable proposal
3. Implementation begins based on the refined proposal
4. `/auto-review-loop` iterates on the actual paper + results

**Can also be used standalone:** If you already have a problem and approach (e.g., from reading papers or from a collaborator's suggestion), invoke directly without running `/idea-creator` first.
