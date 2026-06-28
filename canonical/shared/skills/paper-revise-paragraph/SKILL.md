---
name: paper-revise-paragraph
description: >
  Revise 1-2 paragraphs to address a specific documented issue with full
  traceability. Use when: (1) user says "revise this paragraph", "修改这段",
  "fix this section", "rewrite based on feedback", (2) implementing a single
  fix from revision plan, (3) making targeted manuscript edits with before/after
  comparison. Maximum 2 paragraphs per operation. Outputs original, revised,
  rationale, and verification checklist.
---

# Paragraph Revise

Make targeted manuscript revisions with full traceability.

## Constraints

- **Maximum 2 paragraphs per operation**
- Preserve author's voice and writing style
- Every change must link to a documented issue
- Do not introduce new unsupported claims
- If adding citations, ensure they're verified (use /citation-find first)

## Required Input

Before revising, confirm:
1. **Original text**: The paragraph(s) to modify
2. **Issue ID**: Which review issue this addresses (e.g., W1, S2)
3. **Issue description**: What problem we're fixing
4. **New references**: Any citations to add (from /citation-find)

## Output Format

```markdown
## Issue Being Addressed
**ID**: {issue_id}
**Description**: {issue_description}
**Severity**: [CRITICAL/MAJOR/MINOR]

---

## Original Text
```
[Line N] Original paragraph text here with preserved formatting...
[Line N+1] Second line if applicable...
```

---

## Proposed Revision
```
Revised paragraph text with changes applied...
New sentences or modified content...
```

---

## Modification Rationale

| Aspect | Details |
|--------|---------|
| **What changed** | [Specific description of changes made] |
| **Why** | Addresses Issue {ID}: {brief reason} |
| **New references** | {citation keys added, or "None"} |
| **Words added/removed** | +X / -Y words |

---

## Verification Checklist
- [ ] Directly addresses the documented weakness
- [ ] Maintains logical flow with surrounding paragraphs
- [ ] New citations properly formatted (\cite{key})
- [ ] No new unsupported claims introduced
- [ ] Consistent with author's writing style
- [ ] Technical accuracy preserved
```

## Style Preservation Guidelines

### Analyze before revising
- Sentence length patterns (short/long/mixed)
- Voice (active/passive preference)
- Technical density
- Transition word usage
- First person usage (we/our vs. passive)

### Match the original
- If author uses short sentences → keep concise
- If author uses passive voice → maintain it
- If author avoids "we" → don't introduce it
- If author uses hedging (may, might, could) → preserve uncertainty level

## When New References Are Needed

If revision requires new citations:

1. **First**: Run `/citation-find` to get verified quotes
2. **Then**: Run `/citation-assistant` to add to .bib file
3. **Finally**: Include `\cite{key}` in revised text

Do NOT add citations without verified supporting quotes.

## HITL Checkpoint

After presenting the revision, wait for user decision:
- **Accept**: Apply the change
- **Modify**: User provides adjustment, regenerate
- **Skip**: Move to next issue without this change

## Multiple Paragraph Handling

If a fix spans more than 2 paragraphs:
1. Identify the 2 most critical paragraphs
2. Revise those first
3. Note remaining paragraphs for subsequent operation
4. Chain multiple /paper-revise-paragraph calls if needed
