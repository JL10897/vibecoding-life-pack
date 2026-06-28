---
name: revision-plan
description: >
  Convert review feedback into prioritized, tiered revision plan. Use when:
  (1) user has review comments from /paper-review or external reviewers,
  (2) user says "plan my revisions", "制定修改计划", "prioritize fixes",
  "what should I fix first", (3) organizing manuscript changes by importance,
  (4) creating actionable revision roadmap. Outputs 4-tier plan with
  dependencies and scope estimates.
---

# Revision Plan

Transform review feedback into structured, prioritized modification plan.

## Input Required

- Review report (from /paper-review or external reviewer comments)
- Original manuscript structure (sections, page count)

## Process

1. Extract all weaknesses (W1, W2...) and suggestions (S1, S2...)
2. Classify each into one of 4 tiers based on severity
3. Identify dependencies between fixes
4. Estimate scope for each item
5. Determine execution order within and across tiers

## Tier Definitions

| Tier | Name | Criteria | Fix Order |
|------|------|----------|-----------|
| 1 | Critical | Undermines core claims, must fix | First |
| 2 | Major | Significant quality impact | Second |
| 3 | Minor | Improves but not blocking | Third |
| 4 | Polish | Language, formatting, consistency | Last |

## Output Format

```markdown
# Revision Plan for: {Paper Title}

Generated from: {review source}
Total issues: {N} ({X} Critical, {Y} Major, {Z} Minor)

---

## Tier 1: Critical Issues (Fix First)

| ID | Issue | Location | Scope | Depends On | New Sources? |
|----|-------|----------|-------|------------|--------------|
| W1 | Core claim unsupported | Sec 4.2 | 2 para | - | Yes |
| W2 | Method description unclear | Sec 3.1 | section | - | No |

---

## Tier 2: Major Issues

| ID | Issue | Location | Scope | Depends On | New Sources? |
|----|-------|----------|-------|------------|--------------|
| W3 | Missing ablation study | Sec 4.3 | 1 para | W1 | No |
| S1 | Add baseline comparison | Sec 4.1 | 2 para | - | Yes |

---

## Tier 3: Minor Issues

| ID | Issue | Location | Scope | Depends On | New Sources? |
|----|-------|----------|-------|------------|--------------|
| W4 | Figure 3 readability | Page 6 | figure | - | No |
| W5 | Related work gap | Sec 2 | 1 para | - | Yes |

---

## Tier 4: Final Polish

| ID | Issue | Location | Scope | Depends On | New Sources? |
|----|-------|----------|-------|------------|--------------|
| - | Language consistency | All | pass | All above | No |
| - | Citation format check | All | pass | All above | No |

---

## Recommended Execution Order

1. **W1** (Critical) - Address first, provides foundation
2. **W2** (Critical) - Method clarity needed for other fixes
3. **W3** (Major) - Depends on W1 completion
4. **S1** (Major) - Independent, can parallelize
5. **W5** (Minor) - Adds context
6. **W4** (Minor) - Visual improvement
7. **Tier 4 pass** - After all content changes

---

## Estimated Effort

| Tier | Items | Paragraphs | New Sources |
|------|-------|------------|-------------|
| 1 | 2 | ~4 | 1-2 papers |
| 2 | 2 | ~3 | 1 paper |
| 3 | 2 | ~2 | 1 paper |
| 4 | - | full pass | 0 |

---

## Notes

- {Any special considerations}
- {Potential conflicts between suggestions}
- {Items that may require author decision}
```

## Minimal Intervention Principle

**Constraint**: Always prefer the smallest change that fully addresses the issue.

- If adding **one sentence** can fix it, don't rewrite the paragraph
- If adding **one paragraph** can fix it, don't restructure the section
- If **reordering** existing content works, don't create new content
- Preserve the author's voice and existing structure as much as possible

When planning scope, ask: "What is the *minimum* edit needed to resolve this issue?"

Examples:
- Gap-Contribution misalignment → Add 1-2 bridging sentences, not rewrite Introduction
- Missing definition → Insert definition on first use, not restructure terminology throughout
- Figure caption insufficient → Expand caption text, not redesign figure

## Scope Estimates

- `+1 sent` - Add/modify single sentence
- `1 para` - Single paragraph change
- `2 para` - Up to 2 paragraphs
- `section` - Significant section rewrite (use sparingly)
- `multi-sec` - Spans multiple sections (rare, requires justification)
- `figure` - Figure/table modification
- `pass` - Full document pass

## Dependency Notation

- `-` = No dependencies, can start immediately
- `W1` = Must complete W1 first
- `W1, S2` = Depends on multiple items
- `All above` = Depends on all previous tiers

## HITL Checkpoint

After presenting the plan, ask user to:
1. Confirm tier assignments are correct
2. Adjust priority order if needed
3. Remove items they choose not to address
4. Add any missing issues

Then proceed with /paragraph-revise for each item in order.

## Execution Pacing (One-at-a-Time Rule)

**Constraint**: When executing revisions, process **ONE issue (W/S) at a time**.

**Workflow per issue:**
1. **Present**: Show the issue ID, description, and proposed fix
2. **Preview**: Display the exact edit (before → after) or scope of change
3. **Wait**: Get explicit user approval before applying
4. **Apply**: Make the change only after approval
5. **Confirm**: Show completion, then ask "Ready for next? (W{N+1})"

**Why**: Batch-editing all issues at once is too fast for quality control. User needs to:
- Verify each fix matches their intent
- Catch any unintended side effects
- Maintain mental model of changes

**Format for presenting each issue:**
```
---
## W{N}: {Issue Title}

**Location**: {file.tex, Section X}
**Scope**: {+1 sent / 1 para / etc.}

**Problem**: {Brief description}

**Proposed Fix**:
```latex
% BEFORE
{existing text}

% AFTER
{modified text}
```

Ready to apply? (y/n/modify)
---
```

**Never** apply multiple W fixes in a single response without per-item approval.
