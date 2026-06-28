---
name: paper-review
description: >
  Perform structured academic paper review with evidence-based critique.
  Use when: (1) reviewing a paper PDF or LaTeX source, (2) user says
  "review my paper", "审稿", "给我的论文提意见", "critique this manuscript",
  (3) generating feedback before revision, (4) simulating peer review for
  ML/AI/NLP venues (ACL, EMNLP, NeurIPS, ICLR, CVPR, etc.) or
  robotics/HRI venues (RO-MAN, HRI, ICSR, IROS, ICRA). Produces
  structured output with severity-tagged weaknesses and evidence anchors.
---

# Paper Review

Generate structured academic review with evidence anchors for every claim.

## Output Format

Use exactly these sections in order:

1. **Synopsis of the paper** - 2-3 sentence summary of contribution
2. **Summary of Review** - Overall assessment without scores
3. **Strengths** - Bullet points with evidence anchors and [STRONG]/[MODERATE] tags
4. **Weaknesses** - Bullet points with evidence anchors and severity tags
5. **Suggestions for Improvement** - Actionable recommendations linked to weaknesses
6. **References** - Only cite items from manuscript's reference list

## Severity Tags

Apply to each weakness:
- `[CRITICAL]` - Core claims unsupported, methodology flawed, must fix
- `[MAJOR]` - Significant quality impact, strongly recommended to fix
- `[MINOR]` - Improvement suggestion, nice-to-have

## Revision Confirmation Protocol

When implementing fixes based on review findings, follow these confirmation requirements:

- **[CRITICAL] issues**: Break down into smaller, manageable sub-fixes. Do not attempt to resolve the entire critical issue in one edit. Present each sub-fix individually, wait for user confirmation, then proceed to the next sub-fix. This ensures precision and avoids compounding errors.
- **[MAJOR] issues**: Require individual confirmation for each fix. Present the proposed change, wait for user approval (e.g., "y", "ok", "proceed"), then implement.
- **[MINOR] issues**: May be fixed directly without individual confirmation. Batch multiple minor fixes together and report what was changed afterward.

## Evidence Anchor Format

Every point must reference: `(Section X.X)`, `(Figure Y)`, `(Table Z)`, `(Eq. N)`, `(Page P, Line L)`

If no evidence exists, write: "No direct evidence found in manuscript."

## Venue-Specific Standards

For venue-specific criteria (statistical significance requirements, reproducibility
checklists, page limits), see [venue-guidelines.md](references/venue-guidelines.md).

## Severity Classification Details

See [severity-criteria.md](references/severity-criteria.md) for detailed examples of each severity level.

## Quality Checklist

Always verify these aspects during review. The checklist is organized into two tiers:

- **Tier A (四层审视 / Four-Layer Scrutiny)**: High-level epistemological examination — assess whether the paper's premise, design, execution, and communication each hold up under scrutiny. These questions should shape the **Summary of Review** and drive the most important **Weaknesses**.
- **Tier B (Craft Checklist)**: Fine-grained craft checks for structural, presentational, and analytical quality. These feed into **Weaknesses** and **Suggestions for Improvement**.

---

### Tier A: Four-Layer Scrutiny (四层审视)

#### A1. 前提层 — Premise Layer

Ask these questions before evaluating anything else:

1. **Problem Existence**: Does the problem this paper addresses genuinely exist? Is there real-world or research-community evidence that this is an actual need, not a manufactured one? Flag papers that solve problems no one has.
2. **Formulation Assumptions**: Does the problem formulation carry hidden assumptions? Are these assumptions explicitly stated and justified? (e.g., assuming user preferences are static, assuming a particular data distribution, assuming annotation quality)
3. **Philosophical Risks / Counter-Arguments**: Are there fundamental objections or alternative perspectives that the paper ignores? (e.g., "Is this task even well-defined?", "Does the metric actually measure what it claims?", "Could the entire framing be flawed?") Flag missing engagement with known counter-arguments in the field.

#### A2. 设计层 — Design Layer

Scrutinize key design decisions:

4. **Theoretical / Empirical Grounding of Design Choices**: Is every key design choice (taxonomy categories, evaluation dimensions, model architecture decisions, loss function, annotation scheme) grounded in prior literature, theory, or principled justification? Flag unjustified design choices that appear arbitrary.
5. **Why This, Not That?**: For each major design decision, has the paper considered and argued against alternatives? (e.g., "Why these 5 dimensions and not 3 or 8?", "Why this taxonomy granularity?", "Why this evaluation protocol over another?") Flag designs presented as obvious when alternatives exist.
6. **Coverage and Extensibility**: Does the paper discuss the coverage (what's included) and boundaries (what's excluded) of its design? Is the framework extensible to new domains, languages, or tasks? Flag designs that appear closed or brittle without acknowledgment.

#### A3. 执行层 — Execution Layer

Verify that claims are fully backed by evidence:

7. **Claim–Evidence Alignment**: Does every claim in the paper have a corresponding table, figure, or formal argument that directly supports it? Flag claims that lack direct evidence or rely on hand-waving.
8. **Anomaly Acknowledgment**: Are there anomalous or unexpected results? If so, are they acknowledged and explained rather than silently ignored? Flag cherry-picked reporting where inconvenient results are buried or absent.
9. **Ablation / Comparison Completeness**: Are the key ablation studies and baseline comparisons complete? Can the reader attribute observed improvements to specific design choices? Flag missing ablations that would be obvious to reviewers.
10. **Reproducibility**: Are sufficient details provided (hyperparameters, data splits, random seeds, compute requirements, code availability) for independent reproduction? Flag papers where key experimental details are missing or vague.

#### A4. 传达层 — Communication Layer

Assess whether the paper effectively communicates its contributions:

11. **Illustrative Examples**: Are there enough concrete examples (input/output pairs, case studies, walkthroughs) for a reader unfamiliar with the subfield to understand the approach? Flag papers that remain purely abstract without grounding.
12. **Define-on-First-Use**: Are all key terms, acronyms, and novel concepts defined when first introduced? (Overlaps with Tier B item 9 — flag here if pervasive.)
13. **Discussion of Implications**: Is there a discussion section (or equivalent) that interprets the results, explains their broader implications, and connects findings to the wider research landscape? Flag papers that end abruptly after results without reflection.
14. **Contribution–Content Alignment**: Do the stated contributions (in Abstract/Introduction) match what the paper actually demonstrates? Flag discrepancies where contributions are overclaimed relative to the evidence presented, or where significant work done in the paper is not highlighted as a contribution.

---

### Tier B: Craft Checklist

#### Layer 1: Structural Coherence (Narrative Flow)

1. **Narrative Arc Alignment**: Check if the story flows consistently from problem → method → validation. The framing established in Introduction should carry through to Conclusion without mid-paper shifts.

2. **Gap → Contribution → Validation Triangle**: Verify the closed loop:
   - Each identified gap has a corresponding contribution
   - Each contribution has corresponding experiments/results that validate it
   - No "orphan gaps" (raised but unaddressed) or "orphan contributions" (claimed without prior motivation)

3. **Related Work ↔ Experiments Correspondence**:
   - Baselines/prior methods discussed in Related Work should appear in experimental comparisons
   - Claimed novelty should be clearly positioned against prior work

4. **Method → Result → Analysis Chain**:
   - Each method component should have corresponding results (main results or ablation)
   - Analysis insights should be grounded in presented results, not appearing from nowhere

5. **Reader Expectation Management**:
   - Expectations set up in earlier sections should be fulfilled later
   - No sudden introduction of concepts/methods/metrics without prior setup

#### Layer 2: Claim Coherence (Consistency of Claims)

6. **Cross-Section Claim Consistency**: Verify claims align across:
   - Abstract ↔ Introduction ↔ Conclusion
   - No overclaiming (results don't support claim) or underclaiming (results exist but not emphasized)

7. **Limitation-Awareness Consistency**:
   - Limitations section should correspond to actual method/experiment constraints
   - No obvious limitations omitted that reviewers would immediately spot

#### Layer 3: Presentation Quality

8. **Terminology Consistency**: Check if key terms are used consistently across all sections. Flag terms that appear with different names/definitions without clarification (e.g., "user preference" vs "interaction preference" vs "UX preference").

9. **Define-Before-Use**: All key concepts, terms, abbreviations, and methods must be defined before use. Flag:
   - Acronyms used before expansion
   - Technical terms used without definition
   - Methods or metrics referenced before explanation

10. **No Orphan Concepts**: Everything introduced must be explained; if it cannot be explained, it should not appear. Flag:
    - Ground-truth mentioned without explaining its source
    - Metrics used without defining how they are computed
    - Components referenced but never elaborated
    - Numbers/statistics cited without context or justification

11. **Abstraction Level Appropriateness**: Match detail level to context.
    - **Introductions and overviews**: Avoid specific numbers that distract from core concepts (e.g., "31 settings spanning 14 attributes" → "a hierarchical taxonomy across four dimensions")
    - **Method sections**: Specific numbers are appropriate and expected
    - Flag: Numeric details in programmatic/overview statements that prompt "why these numbers?" questions

12. **New Terms Need Operational Definitions**: Novel terminology or paradigms must be operationally defined, not just branded. Flag:
    - Terms introduced without explaining what they mean in practice
    - ❌ "We propose the XYZ paradigm" (branding only)
    - ✅ "We propose the XYZ paradigm, where [concrete mechanism]"

13. **Avoid Laundry Lists in Intro/Related Work**: Introduction and Related Work should synthesize, not enumerate.
    - ❌ Listing categories with citations without sharp contrast
    - ✅ Summarize landscape, then state what's missing
    - Detailed enumeration belongs in Method or Appendix

14. **Word Choice Appropriateness**: Flag exaggerated, overstated, or inappropriate word choices. Examples:
   - "principles" when describing design choices or guidelines
   - "novel" or "first" without proper literature support
   - "significant" without statistical backing
   - "optimal" or "best" without comparative evidence
   - "paradigm shift" or "revolutionary" for incremental improvements
   - Hedging language that weakens claims unnecessarily (e.g., "seems to", "might possibly")

   Also flag overly formal or uncommon words that can be simplified:
   | Avoid | Prefer |
   |-------|--------|
   | comprising | which integrates / that combines |
   | abound | (use common alternatives) |
   | we argue that | (state directly) |
   | enabling... (as gerund in complex sentence) | This enables... (simple sentence) |

#### Layer 4: Figure & Table Quality

15. **Figure Quality**:
    - **Caption self-containment**: Can readers understand the figure without reading body text? Caption should be concise yet informative.
    - **Caption-content alignment**: Does the caption accurately describe what the figure shows?
    - **Visual clarity**: Readable font sizes, clear legends, appropriate color choices, no clutter
    - **Narrative integration**: Is the figure explicitly referenced and discussed in text?

16. **Table Quality**:
    - **Format clarity**: Clear headers, appropriate alignment, logical row/column organization
    - **Caption informativeness**: Explains what the table presents and key takeaways
    - **Readability**: Not overcrowded, appropriate use of bold/highlighting for key values
    - **Unit consistency**: All values have clear units where applicable
    - **Narrative integration**: Is the table explicitly referenced and discussed in text?

17. **Figure/Table Necessity**: Each visual element should earn its space—no redundant figures/tables that merely repeat text content

#### Layer 5: Results & Analysis Quality

Results and Analysis sections distinguish "acceptable" from "excellent" papers. Avoid the "data dump" anti-pattern—listing numbers without narrative structure.

18. **Narrative Structure Around Research Questions**:
    - **Hierarchical presentation**: Present most important/core findings first, then secondary/auxiliary results
    - **Progressive connection**: Each result should set up the next analysis. Good pattern: "We observed phenomenon A (result) → To investigate A's cause, we further tested B (transition) → We found that..."
    - **RQ-driven organization**: Results should directly address stated research questions in logical order
    - Flag: Disconnected subsections that read like separate mini-papers

19. **Results–Visual Integration**:
    - **No verbatim repetition**: Text should interpret, not recite tables/figures
      - ❌ Bad: "Table 1 shows A is 50, B is 60, C is 70."
      - ✓ Good: "As shown in Table 1, C significantly outperforms A ($p < 0.05$), exhibiting a clear upward trend."
    - **Appropriate chart selection**: Bar charts for comparison, line charts for trends, box plots for distributions
    - **Professional aesthetics**: Distinguishable colors, readable fonts, no clutter

20. **Description vs. Interpretation Separation**:
    - **Results (what happened)**: Objective, past tense, reports data changes, statistical significance ($p$-values), effect sizes. No emotional language.
    - **Analysis/Discussion (what it means)**: Interprets findings, connects to hypotheses, explains mechanisms, acknowledges limitations
    - Flag: Mixing interpretation into Results section or presenting Analysis without grounding in presented data

21. **Statistical Rigor and Honesty**:
    - **Complete reporting**: Mean, standard deviation, confidence intervals where appropriate
    - **No over-interpretation**: Statistically non-significant differences cannot be claimed as meaningful differences
    - **Effect size awareness**: Statistical significance alone is insufficient; practical significance matters
    - **Honest negative results**: Acknowledge when hypotheses are not supported rather than spinning or omitting
    - Flag: Cherry-picking favorable metrics while ignoring unfavorable ones

22. **Analysis Depth Indicators**:
    - **Beyond surface patterns**: Analysis should explain *why* results occur, not just *what* occurred
    - **Cross-result synthesis**: Connect findings across different experiments/tables
    - **Limitation acknowledgment**: Discuss what results cannot conclude
    - Flag: Analysis that merely restates results in different words without adding insight

## Constraints

- No scores, ratings, or accept/reject verdicts
- Maintain anonymity and constructive tone
- Do not cite external sources unless in manuscript's references
- Do not speculate about author identity
- **Ignore LaTeX comments**: When reviewing .tex source files, skip all commented lines (starting with `%`). These are author notes, not part of the submitted manuscript. Only review the actual compiled content.

## Example Output Structure

```markdown
## Synopsis of the paper
This paper proposes [method] for [task], achieving [result] on [benchmark].

## Summary of Review
The paper addresses an important problem with a novel approach. However,
several methodological concerns and missing experiments limit the strength
of the claims.

## Strengths
- [STRONG] Novel architecture design that effectively addresses X (Section 3.2, Figure 2)
- [MODERATE] Comprehensive ablation study covering key components (Table 3)

## Weaknesses
- [CRITICAL] The main claim about Y is not supported by the experiments (Section 4)
- [MAJOR] Missing comparison with Z baseline which is standard in this area (Section 4.1)
- [MINOR] Figure 3 is difficult to read due to small font size (Page 6)

## Suggestions for Improvement
1. Add experiments comparing with Z to validate the claimed improvements (addresses W2)
2. Include statistical significance tests (p-values or confidence intervals) for main results
3. Improve Figure 3 readability by increasing font size and adding legends

## References
- [1] Author et al., 2023 (cited in Section 2 for baseline comparison)
```
