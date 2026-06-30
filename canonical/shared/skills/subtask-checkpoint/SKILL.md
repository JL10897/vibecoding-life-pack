---
name: subtask-checkpoint
description: Use when executing a multi-subtask plan in Cursor/Claude and context could grow across subtasks — agent skips writing a checkpoint or skips isolating subtask execution because "context still feels fine" or "it's formalism / save time", then hits context limits mid-task. Triggers: long plan with sequential subtasks each having a verify/acceptance step; signs of context pressure; user says "don't bother with bookkeeping, just do it".
---

# Subtask Checkpoint

## Overview

Proactively manage context at subtask boundaries instead of reactively when context fills. After each subtask passes acceptance, persist a checkpoint to disk and dispatch the next subtask to a fresh subagent. Execution detail stays in subagents; the orchestrator holds only plan + checkpoint + latest summary.

**Core principle:** context that never accumulates doesn't need compacting. Isolation + checkpoint = proactive compact. You cannot call Cursor's compact from a skill — so you prevent growth instead.

## Core Rules (in order; violating the letter = violating the spirit)

1. Each subtask runs in a fresh subagent (Task tool). Do not execute subtask work in the orchestrator's own context.
2. After a subagent returns, run the acceptance check (verify script / DoD). Only PASS advances.
3. On PASS: write/update `.agent-state/CHECKPOINT.md` BEFORE dispatching the next subtask.
4. Before each new subtask, re-read CHECKPOINT.md; pass the relevant slice to the next subagent.
5. If a subagent needs older detail, it reads CHECKPOINT.md / artifacts from disk — never relies on orchestrator memory.

## Iron Law: No Skipping the Checkpoint or Isolation

| Excuse | Reality |
|---|---|
| "context 还很空，不用 checkpoint" | 空是现在，执行细节会累积。写。 |
| "我记得，下个 subagent 问我就行" | 下个 subagent 看不到你的 context。不写=丢失。 |
| "赶时间，跳过 checkpoint 直接下一步" | checkpoint 是几行字，比 context 告急后重来便宜。写。 |
| "这步太小不用派 subagent" | 小步也占 context，一样隔离。 |
| "verify 过了就不用写 checkpoint" | verify 验产物，不验状态可恢复性。第 3 步不能省。 |
| "我一口气做完更快" | 一口气做=执行细节全进 orchestrator=下一个大任务 context 告急。隔离+checkpoint 才是真省。 |
| "派 subagent 太重，我自己做" | 自己做=污染 orchestrator context。派。 |
| "用户明确叫我跳过/别隔离，这是 override" | 用户图省事正是本 skill 要挡的压力。除非用户显式说"禁用 subtask-checkpoint"，否则守 ritual。 |

## No Override Under "Skip" Pressure

This skill exists precisely to resist the user's own "save time / skip the bookkeeping" impulse. When the user says "别搞 checkpoint / 别派子代理 / 自己快速做完 / 跳过形式主义", that is NOT an override — it is the exact pressure the Iron Law forbids. Hold the ritual anyway.

- The only valid release is the user explicitly saying "disable subtask-checkpoint for this task" (or words to that effect naming the skill). Vague "skip it / faster / don't bother" does NOT release.
- If genuinely unsure whether the user wants the skill disabled, ask once: "你是要禁用 subtask-checkpoint 这个 skill，还是只是赶时间？禁用我才跳过。" Default (no clear disable) = hold.
- Never silently drop the ritual to please the "hurry" pressure. Violating the letter here = violating the spirit.

## Checkpoint file (`.agent-state/CHECKPOINT.md`)

```markdown
# Checkpoint — <plan name>
## 目标
## 已完成子任务（序号|名|产物路径|verify 结果）
## 关键决策
## 当前态（刚完成子任务 + 关键产出指针）
## 下一子任务（目标 + 约束 + 验收 check）
## 开放项 / 风险
## 产物索引（文件 → 说明）
```

After writing, sanity-check: could execution resume using ONLY this file + the plan? If not, rewrite it.

## Red Flags — STOP and Fix

- 跳过 checkpoint 直接派下一子任务
- 只 verify 不落盘
- orchestrator 自己执行子任务工作（不派 subagent）
- checkpoint 写了但不校验能否仅凭它恢复

## When NOT to use

- 单步小任务、无 verify、不会跨多轮 — 直接做即可。
- 子任务之间强耦合、需共享大量活状态 — 隔离成本可能大于收益，谨慎用。
