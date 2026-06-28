---
name: abstract-revise
description: >
  Revise abstract to meet top AI/NLP conference standards (NeurIPS, ICLR, ACL).
  Use when: (1) user says "revise abstract", "重写摘要", "polish abstract",
  (2) after major paper revisions to ensure abstract alignment,
  (3) preparing final submission. Produces hook-gap-contribution structured
  abstract with quantitative validation.
---

# Abstract Revision

Rewrite abstract based on revised paper content, following top AI/NLP conference (NeurIPS, ICLR, ACL) standards: **opening that grabs attention, immediately showing motivation, gap, and contribution**.

## Golden Structure (5-7 sentences)

| Order | Function | Sentences | Requirements |
|-------|----------|-----------|--------------|
| ① **Hook** | Why does this matter? | 1 | Grab attention, establish relevance. NEVER start with "In this paper" |
| ② **Gap** | What's missing? | 1-2 | Specific pain point, not vague |
| ③ **Contribution** | What do we do? | 2-3 | Core innovations, directly address the gap |
| ④ **Validation** | How well does it work? | 1-2 | Key numbers/conclusions, quantitative preferred |
| ⑤ **Availability** | Resource links | Optional | Code/Data/Demo |

## Execution Process

### Step 1: Extract Key Elements
Read the following sections and extract:
- **From Introduction**:
  - The hook (why should readers care?)
  - Identified gaps (what's missing in current work?)
  - Listed contributions (numbered items)
- **From Results/Analysis**:
  - Key quantitative results (improvement %, correlations, reliability scores)
  - Most impressive findings
- **From Conclusion**:
  - Summary claims (must align with abstract)

### Step 2: Cross-Check Alignment
Verify consistency:
- Hook ↔ Introduction first paragraph
- Gap ↔ Introduction gap statements
- Contribution ↔ Introduction contribution list
- Validation ↔ Results/Analysis data
- Terminology ↔ Conclusion wording

### Step 3: Draft New Abstract
Following the golden structure:
1. Write hook sentence (problem-oriented or phenomenon-oriented)
2. State the gap explicitly ("However, X remains...")
3. Introduce contributions with specifics
4. Include quantitative validation
5. Add availability link if applicable

### Step 4: Verify Checklist
- [ ] First sentence does NOT start with "In this paper" or "We propose"
- [ ] Gap appears BEFORE contribution
- [ ] Contributions are specific and verifiable
- [ ] Contains quantitative results
- [ ] Terminology matches Introduction/Conclusion
- [ ] Word count meets venue requirements (ACL: ~250 words, NeurIPS/ICLR: ~300 words)
- [ ] No overclaiming ("novel", "first", "revolutionary" without support)

## Common Problems and Fixes

| Problem | Symptom | Fix |
|---------|---------|-----|
| Weak opening | "In this paper, we propose..." | Change to problem-oriented or phenomenon-oriented hook |
| Missing gap | Jumps directly to "We introduce..." | Add "However, X remains underexplored" before contribution |
| Vague contribution | "a novel framework" | Specify what it does and how |
| No data support | Only qualitative descriptions | Add key metrics (+X%, ρ=0.XX, α=0.XX) |
| Overclaiming | "revolutionary", "first-ever" | Use supported claims, remove exaggerated words |
| Misalignment | Abstract claims ≠ paper content | Re-extract from actual Introduction/Results |

## Output Format

```markdown
## Current Abstract Analysis
- Hook: [present/missing/weak]
- Gap: [present/missing/vague]
- Contribution: [specific/vague]
- Validation: [quantitative/qualitative/missing]
- Issues: [list problems]

## Extracted Elements
- **Hook**: [from Introduction]
- **Gap**: [from Introduction]
- **Contributions**:
  1. [contribution 1]
  2. [contribution 2]
  3. [contribution 3]
- **Key Results**: [from Results/Analysis]

## Revised Abstract
[New abstract text following golden structure]

## Verification Checklist
- [x/] First sentence check
- [x/] Gap before contribution
- [x/] Specific contributions
- [x/] Quantitative results
- [x/] Terminology alignment
- [x/] Word count: XXX words
```

## Constraints

- Always read the FULL paper before revising (Introduction, Method, Results, Analysis, Conclusion)
- Never invent claims not supported by paper content
- Preserve technical accuracy over stylistic preference
- Match the paper's actual contribution scope - no overclaiming
- Keep venue word limits in mind
