---
name: revise-plans
description: Revises existing plan documents while preserving logical consistency. Use when iterating requirements, updating an existing plan, adding new requirements to a plan document, checking plan self-consistency, or when the user discusses revising, updating, refining, or extending a plan.
---

# Revise Plans

Use this skill when updating an existing plan document through iterative discussion. The purpose is to keep the plan logically self-consistent while incorporating new requirements.

## Core Rule

Follow this sequence exactly:

```markdown
1. 先考虑现在的 plan 当中有没有不自洽的地方。如果有，先去修正它。
2. 修正完之后，再加入新的需求。
3. 加入新需求后，再去 run 一遍或者重新反思一遍，看现在这个 plan 当中还有没有不自洽或者前言不搭后语的地方。
```

Do not add new requirements before resolving contradictions already present in the current plan, unless the user explicitly asks for a rough draft instead of a coherent revision.

## Revision Workflow

1. Read the current plan document and identify the goal, scope, assumptions, implementation steps, dependencies, risks, and verification criteria.
2. Run a pre-revision consistency pass:
   - Check for contradictions between goals, scope, tasks, and acceptance criteria.
   - Check whether earlier sections conflict with later decisions.
   - Check for terminology drift, duplicated requirements, missing dependencies, impossible ordering, or stale references.
3. Repair the existing plan first:
   - Make the smallest coherent changes that resolve conflicts.
   - Preserve the user's intent and the document's established structure.
   - Ask the user only when a conflict cannot be resolved from context.
4. Add the new requirements:
   - Integrate them into the most relevant sections instead of appending them mechanically.
   - Update affected tasks, dependencies, risks, diagrams, and verification criteria.
   - Remove or revise old text that the new requirements supersede.
5. Run a post-revision consistency pass:
   - Re-read the full plan as a single document.
   - Confirm the added requirements do not introduce contradictions, stale references, missing steps, or scope drift.
   - Confirm the plan still has a clear execution order and validation path.
6. Summarize the revision:
   - Existing inconsistencies fixed.
   - New requirements added.
   - Remaining assumptions or open questions, if any.

## Consistency Checklist

Before finalizing a revised plan, verify:

- The plan has one clear current goal.
- Scope boundaries match the implementation steps.
- Terminology is consistent across the document.
- Earlier sections do not contradict later sections.
- Requirements are represented in tasks and verification steps.
- Dependencies appear before the work that relies on them.
- Removed or superseded ideas are not still referenced elsewhere.
- Open questions are explicit and do not block the claimed plan unless noted.

## Operating Notes

- Respect the current interaction mode. In read-only or planning contexts, propose the revision instead of editing files.
- Keep revisions proportional to the change. Do not rewrite the whole plan when a targeted consistency repair is enough.
- Prefer preserving useful structure over inventing a new template.
- If the plan contains diagrams, tables, or checklists, update them when the revised requirements affect them.
