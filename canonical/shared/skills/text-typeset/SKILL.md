---
name: text-typeset
description: >
  Fix typographic widows - paragraphs ending with only 1-2 words on the last line.
  Use when: (1) user says "fix widows", "调整排版", "calibrate paragraphs",
  (2) preparing final camera-ready submission, (3) polishing PDF layout.
  Compiles PDF, visually inspects for short last lines, and adjusts paragraph
  wording to eliminate widows.
---

# Calibrate One-Two Word (Widow Fix)

Fix typographic "widows" - paragraphs where the last line contains only 1-2 words, which looks awkward in academic papers.

## What is a Widow?

A **widow** in typography refers to a very short last line of a paragraph (typically 1-2 words), which:
- Wastes vertical space
- Looks visually unbalanced
- Is considered poor typesetting practice

## Execution Process

### Step 1: Compile PDF
First compile the document to see current layout:
```bash
cd [project_directory]
pdflatex -interaction=nonstopmode [main].tex
bibtex [main]
pdflatex -interaction=nonstopmode [main].tex
pdflatex -interaction=nonstopmode [main].tex
```

### Step 2: Visual Inspection
Read the compiled PDF and identify paragraphs with widow issues:
- Look for paragraphs ending with only 1-2 words on the final line
- Note the section and approximate location
- Record the problematic text

### Step 3: Fix Strategies

For each widow, choose ONE of these strategies (in order of preference):

| Strategy | When to Use | Example |
|----------|-------------|---------|
| **A. Tighten** | Paragraph has verbose phrases | "in order to" → "to" |
| **B. Expand** | Can add useful detail | Add a clarifying word/phrase |
| **C. Reword** | Neither A nor B works | Restructure the sentence |

#### Strategy A: Tighten (Remove words)
Common phrases to tighten:
- "in order to" → "to"
- "a number of" → "several"
- "due to the fact that" → "because"
- "at this point in time" → "now"
- "in the case of" → "for"
- "is able to" → "can"
- "make use of" → "use"
- Remove unnecessary "that", "very", "really"

#### Strategy B: Expand (Add words)
- Add a clarifying adjective
- Expand an abbreviation
- Add "respectively" or similar
- Include a brief example

#### Strategy C: Reword
- Combine two short sentences
- Split a long sentence
- Change passive to active voice (or vice versa)

### Step 4: Recompile and Verify
After fixes, recompile and verify:
- [ ] Widow is eliminated
- [ ] Meaning is preserved
- [ ] No new widows created
- [ ] Text still reads naturally

## Output Format

```markdown
## Widow Issues Found

| # | Location | Last Line Text | Strategy | Fix |
|---|----------|----------------|----------|-----|
| 1 | Section 3.2, para 2 | "framework." | A (Tighten) | "utilize" → "use" |
| 2 | Section 4.1, para 1 | "results." | B (Expand) | Add "respectively" |

## Fixes Applied

### Fix 1: Section 3.2
**Before**: "...we utilize this framework."
**After**: "...we use this framework."

### Fix 2: Section 4.1
**Before**: "...showing improved results."
**After**: "...showing improved results, respectively."

## Verification
- [x] Recompiled PDF
- [x] All widows eliminated
- [x] No new widows introduced
```

## Constraints

- Preserve meaning exactly - no semantic changes
- Prefer tightening over expanding (saves space)
- Don't fix widows in figure captions or tables (different rules)
- Maximum 3-4 words changed per paragraph
- Re-verify after each fix (fixing one may create another)

## Common Locations for Widows

Widows often appear in:
- End of Introduction (before contributions list)
- End of subsections
- Paragraphs before figures/tables
- Conclusion paragraphs
- Abstract (especially problematic)
