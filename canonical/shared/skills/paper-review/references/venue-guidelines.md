# Venue-Specific Review Guidelines

## ACL/EMNLP/NAACL (ACL Rolling Review)

### Key Criteria
- **Soundness**: Are claims well-supported? Are experiments sufficient?
- **Substance**: Enough content for a full paper?
- **Reproducibility**: Can results be reproduced from the paper?
- **Clarity**: Well-written and well-organized?
- **Knowledge of related work**: Adequate coverage of prior work?

### Statistical Requirements
- Report mean ± std over multiple runs (minimum 3 seeds)
- Include significance tests for main claims
- Use appropriate baselines from the same period

### Reproducibility Checklist
- [ ] Hyperparameters specified
- [ ] Random seeds reported
- [ ] Dataset splits described
- [ ] Compute resources mentioned
- [ ] Code availability stated

---

## NeurIPS/ICML/ICLR

### Key Criteria
- **Novelty**: New ideas, methods, or insights?
- **Quality**: Technically sound and well-executed?
- **Clarity**: Clear presentation?
- **Significance**: Important contribution to the field?

### Statistical Requirements
- Error bars or confidence intervals required
- Multiple random seeds (5+ preferred)
- Ablation studies expected for complex methods

### Reproducibility Checklist
- [ ] Full experimental details in paper or appendix
- [ ] Hyperparameter search procedure described
- [ ] Computational cost reported
- [ ] Code/data availability commitment

---

## CVPR/ICCV/ECCV

### Key Criteria
- **Novelty**: Technical innovation?
- **Technical quality**: Sound methodology?
- **Experimental validation**: Sufficient experiments?
- **Presentation**: Clear figures and writing?

### Visual Standards
- High-quality figures with readable labels
- Qualitative results with comparisons
- Architecture diagrams when applicable

### Reproducibility
- Implementation details in supplementary
- Training procedures documented
- Evaluation metrics clearly defined

---

## Common Pitfalls by Venue

### ACL venues
- Missing human evaluation for generation tasks
- Inadequate error analysis
- Over-claiming from limited experiments

### ML venues (NeurIPS/ICML/ICLR)
- Missing theoretical justification
- Incomplete ablations
- No failure case analysis

### Vision venues
- Poor figure quality
- Missing qualitative results
- Unfair baseline comparisons

---

## IEEE RO-MAN / HRI / ICSR (Human-Robot Interaction venues)

Use this section when reviewing for RO-MAN, HRI, ICSR, or any venue where human-robot
interaction, social robotics, or human-subject robotics studies are central. Apply
in **addition to** Tier A / Tier B — do not replace general scrutiny with these checks.

### Key Criteria
- **Research question clarity**: Hypotheses or RQs stated before method, not retrofitted
- **Methodological rigor for human subjects**: Study design appropriate for the RQ
- **Ecological validity**: Does the setup reflect plausible deployment context?
- **Theoretical grounding**: Anchored in HRI / psych / HCI constructs, not just engineering
- **Real-world relevance**: Implications for deployment, design guidelines, or theory

### Human Subjects Methodology Checklist
- [ ] IRB / ethics approval reported
- [ ] Participant N justified (power analysis or convention for study type)
- [ ] Demographics reported: age, gender, prior robot experience, relevant background
- [ ] Recruitment source and compensation disclosed
- [ ] Inclusion / exclusion criteria stated
- [ ] Within- vs between-subjects design justified
- [ ] Counterbalancing / randomization of conditions and order
- [ ] Informed consent procedure described
- [ ] Vulnerable populations (children, elderly, clinical) handled with appropriate safeguards

### Robot Platform & Autonomy Disclosure
- [ ] Platform specified (Pepper, NAO, TIAGo, Baxter, custom, etc.)
- [ ] Sensors / actuators relevant to the study described
- [ ] **Autonomy level** stated: fully autonomous, semi-autonomous, Wizard-of-Oz
- [ ] If WoZ: disclosed clearly and justified; WoZ not presented as autonomous
- [ ] Real robot vs simulation vs video stimuli — justified against the claim
- [ ] Safety protocols for physical HRI

### Statistical Requirements (Human-Subject Studies)
- **Appropriate tests for data type**:
  - Likert / ordinal → non-parametric (Wilcoxon signed-rank, Mann-Whitney U, Friedman, Kruskal-Wallis) OR cumulative link models; flag naive t-tests on single Likert items
  - Repeated-measures designs → rmANOVA or mixed-effects models with proper random effects
  - Count / categorical → chi-square, Fisher's exact, logistic regression
- **Effect sizes required**: Cohen's d, η²/η²ₚ, r, or odds ratios — not just p-values
- **Multiple-comparison correction**: Bonferroni, Holm, or FDR when running multiple tests; flag "12 t-tests, 3 significant" without correction
- **Report**: mean, SD, CI (or median/IQR for non-parametric); assumptions checked (normality, sphericity)
- **Small-N honesty**: Do not over-interpret non-significant results in underpowered studies; acknowledge power limitations

### Measurement Quality
- [ ] **Validated instruments** used where available: Godspeed, NASA-TLX, SUS, UEQ, IOS, RoSAS, trust scales (Muir, Schaefer), mind perception, social presence
- [ ] If custom questionnaire: item development, pilot, reliability (Cronbach's α) reported
- [ ] **Inter-rater reliability** for any coded / qualitative data: Cohen's κ, Krippendorff's α, or ICC
- [ ] Construct validity discussed when novel measures introduced

### Qualitative & Mixed Methods
- [ ] Analysis approach named (thematic analysis, grounded theory, IPA, content analysis) and cited
- [ ] Coding procedure described (open/axial, deductive/inductive, codebook development)
- [ ] Saturation or stopping criterion addressed
- [ ] Reflexivity / researcher positionality acknowledged where relevant

### Ecological Validity Checks
- **Setting**: in-lab vs in-the-wild; one-shot vs longitudinal
- **Task realism**: contrived lab task vs authentic interaction
- **Interaction duration**: minutes vs hours vs weeks — matched to claim
- **Generalization scope**: flag claims that exceed the studied population / context

### Theoretical Grounding
Flag papers that present an HRI study without engaging relevant constructs where they apply:
- Trust, reliance, compliance
- Anthropomorphism, mind perception, uncanny valley
- Social presence, co-presence, telepresence
- CASA (Computers Are Social Actors), media equation
- Mental models, theory of mind, common ground
- Proxemics, gaze, turn-taking (for interaction dynamics)

A purely engineering framing ("we built X, users liked it") without theoretical anchoring
is a **[MAJOR]** weakness for RO-MAN/HRI venues.

### Reproducibility (HRI-specific)
Code is often less central than **protocol**. Expect:
- [ ] Study protocol / script
- [ ] Stimuli (videos, robot behaviors, dialogue) shared or described in detail
- [ ] Full questionnaire items (in appendix or supplementary)
- [ ] Robot behavior specification (state machine, policy, or Wizard script)
- [ ] Analysis code / scripts where applicable

### Novelty Calibration
**Do not apply "must beat SOTA" framing.** Valid RO-MAN contributions include:
- Novel interaction design with rigorous evaluation
- Replication / extension to new population (children, elderly, clinical, cross-cultural)
- Replication / extension to new context (home, hospital, classroom, public space)
- Longitudinal studies of previously short-term findings
- Null / negative results with methodological rigor
- New measurement instruments or evaluation protocols
- Design guidelines derived from empirical study

### Common Pitfalls at RO-MAN / HRI
- Wizard-of-Oz presented as autonomous system
- Convenience sample of undergraduates generalized to "users"
- Likert items analyzed with parametric tests without justification
- Multiple comparisons without correction
- No effect sizes, only p-values
- Custom questionnaire with no reliability data
- Single-session lab study making deployment claims
- Engineering paper with a tacked-on "user study" (N=8, no real analysis)
- Claims about trust / anthropomorphism / social presence without using established measures
- Video-only or simulation-only study claiming findings about embodied interaction
