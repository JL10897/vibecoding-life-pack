# Severity Classification Criteria

## [CRITICAL] Issues

Must be fixed for the paper to be acceptable. These undermine the core contribution.

### Examples

**Logical/Methodological**
- Main claim contradicted by the paper's own results
- Fundamental flaw in experimental design (e.g., data leakage, test set contamination)
- Circular reasoning in the argument
- Core assumption stated but never validated

**Evidence Gaps**
- Central claim with zero supporting evidence
- Results presented without any reproducibility information
- Key baseline missing that would invalidate the comparison

**Technical Errors**
- Incorrect mathematical derivation that affects conclusions
- Bug in algorithm description that would prevent reproduction
- Misuse of evaluation metrics

### How to Identify
Ask: "If this issue is not fixed, can the paper's main contribution still stand?"
If NO → [CRITICAL]

---

## [MAJOR] Issues

Significantly affect paper quality but don't invalidate the core contribution.

### Examples

**Incomplete Experiments**
- Missing ablation for a key component
- Standard baseline not included (but others are)
- No statistical significance testing
- Limited dataset coverage

**Reproducibility Concerns**
- Hyperparameters not fully specified
- Training details unclear
- Random seeds not reported
- Compute requirements not mentioned

**Related Work Gaps**
- Important prior work not cited
- Relationship to concurrent work not discussed
- Claims of novelty that overlap with existing work

**Clarity Issues (Severe)**
- Method description too vague to understand
- Figure essential to understanding is unreadable
- Notation inconsistent throughout

### How to Identify
Ask: "Does this significantly weaken the paper even if the core idea is valid?"
If YES → [MAJOR]

---

## [MINOR] Issues

Would improve the paper but not essential.

### Examples

**Presentation**
- Typos and grammatical errors
- Figure could be improved but is readable
- Some sections could be reorganized
- Font sizes in figures slightly small

**Nice-to-Have Experiments**
- Additional datasets would strengthen but aren't required
- More analysis would be interesting
- Comparison with tangentially related work

**Style**
- Writing could be more concise
- Some redundancy in explanations
- Abstract could be more informative

### How to Identify
Ask: "Is this a 'nice to have' rather than 'need to have'?"
If YES → [MINOR]

---

## Edge Cases

### When severity depends on venue
- Missing code: [MINOR] for theory venues, [MAJOR] for systems venues
- Human evaluation: [CRITICAL] for generation tasks, [MINOR] for classification

### When to escalate
- Multiple [MINOR] issues in same area → consider [MAJOR]
- Pattern of [MAJOR] issues suggesting deeper problem → consider [CRITICAL]

### When to de-escalate
- Issue acknowledged and discussed by authors → lower severity
- Limitation is inherent to the problem setting → consider [MINOR]
