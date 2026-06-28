---
name: paper-revise-verify
description: >
  Cross-check manuscript revisions against original review feedback.
  Use when: (1) user says "verify my changes", "检查修改", "revision check",
  "did I address all feedback", (2) completing a revision tier and need
  verification, (3) final quality check before submission. Produces
  verification report with resolution status for each original issue.
  This is the workflow endpoint.
---

# Verify Revisions

Confirm all review issues have been properly addressed. This is the final
checkpoint before considering the revision complete.

## Process

1. Load original review report
2. Load modification log (all changes made)
3. For each weakness/suggestion:
   - Locate corresponding modification(s)
   - Verify modification adequately addresses the concern
   - Check for introduced inconsistencies
4. Run consistency checks
5. Generate verification report

## Input Required

- **Original review**: From /paper-review or external source
- **Modification log**: List of all /paper-revise-paragraph operations
- **Current manuscript**: Path to revised document

## Output Format

```markdown
# Verification Report

**Paper**: {title}
**Review Source**: {/paper-review or external}
**Revisions Made**: {N} paragraphs modified
**Date**: {timestamp}

---

## Resolution Summary

| Status | Count |
|--------|-------|
| ✅ Fully Resolved | {X} |
| ⚠️ Partially Resolved | {Y} |
| ❌ Unresolved | {Z} |
| 🔍 New Issues | {W} |

---

## ✅ Fully Resolved ({X} items)

| Issue ID | Original Concern | Resolution | Location |
|----------|------------------|------------|----------|
| W1 | Core claim unsupported | Added experimental evidence | Sec 4.2, ¶2-3 |
| W2 | Missing baseline | Added comparison with X | Table 2 |

---

## ⚠️ Partially Resolved ({Y} items)

| Issue ID | Original Concern | What's Done | What Remains |
|----------|------------------|-------------|--------------|
| W3 | Incomplete ablation | Added 2 of 3 suggested | Third ablation TBD |

---

## ❌ Unresolved ({Z} items)

| Issue ID | Original Concern | Reason |
|----------|------------------|--------|
| S2 | Add human evaluation | User chose to skip |
| W5 | Missing statistical tests | Requires re-running experiments |

---

## 🔍 New Issues Detected

- Inconsistency: Section 3 now references Figure 4, but Figure 4 caption unchanged
- Citation [23] added but not in .bib file

---

## Consistency Check

### Citations
- [x] All \cite{} keys exist in .bib
- [x] No orphaned .bib entries (optional check)
- [ ] Citation [NewRef2024] missing from .bib ⚠️

### Cross-References
- [x] All figure references valid
- [x] All table references valid
- [x] All equation references valid
- [x] Section numbering consistent

### Content Consistency
- [x] Abstract matches paper content
- [x] Contributions in intro match conclusions
- [ ] Related work mentions method X but method section doesn't ⚠️

---

## Recommendation

{One of the following}

### ✅ COMPLETE
All critical and major issues resolved. Paper ready for resubmission.

### ⚠️ MOSTLY COMPLETE
{X} minor issues remain. Recommend addressing before submission:
- {list issues}

### 🔄 NEEDS MORE WORK
{X} critical/major issues unresolved. Recommend returning to:
- {list issues with suggested actions}
```

## Verification Logic

### Fully Resolved
- Modification directly addresses the documented weakness
- Evidence anchor in revision matches review complaint
- No new issues introduced by the fix

### Partially Resolved
- Issue was addressed but incompletely
- Only part of the suggestion was implemented
- Fix may need expansion

### Unresolved
- No modification found for this issue
- User explicitly skipped
- Outside scope (e.g., requires new experiments)

## Consistency Checks

### Citation Consistency
```bash
# Extract all \cite{} from .tex
grep -oP '\\cite\{[^}]+\}' manuscript.tex

# Compare with .bib entries
```

### Cross-Reference Validity
- Check all `\ref{}` have corresponding `\label{}`
- Check figure/table numbers sequential
- Check no dangling references

## HITL Checkpoint

After presenting report:
1. **Complete** → Workflow ends
2. **Return for fixes** → Go back to /paper-revise-paragraph for specific issues
3. **Accept with notes** → Mark as complete with documented exceptions
