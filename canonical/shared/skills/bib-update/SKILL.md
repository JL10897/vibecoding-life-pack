---
name: bib-update
description: >
  Add or update references in .bib file with proper BibTeX formatting.
  Use when: (1) user says "add to bibliography", "更新bib", "add citation",
  "update references", (2) new source found via /find-sources needs adding,
  (3) managing LaTeX bibliography files, (4) fixing citation format issues.
  Integrates with Zotero for automatic BibTeX export. Validates syntax and
  prevents duplicates.
---

# Bib Update

Manage .bib file entries with validation and duplicate prevention.

## Process

1. Identify source (Zotero item key or manual BibTeX)
2. Check for duplicates in target .bib file
3. Generate citation key following convention
4. Validate BibTeX syntax
5. Append to .bib file
6. Return citation key for use in manuscript

## Input Required

- **Source**: Zotero item key OR manual BibTeX entry
- **Target .bib file**: Path to bibliography file
- **Citation key preference**: (optional) Custom key format

## Output Format

```markdown
## Added Entry

```bibtex
@article{SmithJones2024,
  author = {Smith, John and Jones, Jane},
  title = {A Novel Approach to Something Important},
  journal = {Journal of Important Research},
  year = {2024},
  volume = {42},
  number = {3},
  pages = {123--145},
  doi = {10.1234/example.2024}
}
```

## Citation Key
`SmithJones2024`

## Usage in LaTeX
```latex
\cite{SmithJones2024}
```

## Updated File
`/path/to/references.bib`

## Validation
- [x] BibTeX syntax valid
- [x] No duplicate entry found
- [x] Required fields present
```

## Citation Key Convention

Format: `{FirstAuthorLastName}{SecondAuthorLastName}{Year}`

| Authors | Example Key |
|---------|-------------|
| Single author | `Smith2024` |
| Two authors | `SmithJones2024` |
| Three+ authors | `SmithEtAl2024` |

### Handling Conflicts
If key exists, append letter: `Smith2024a`, `Smith2024b`

## From Zotero

```python
# Get BibTeX from Zotero item
zotero_get_item_metadata(item_key="ABC123", format="bibtex")
```

## Duplicate Check

Before adding, search existing .bib for:
1. **Same DOI** - Exact match → skip with notice
2. **Same title** - Fuzzy match (>90%) → warn user
3. **Same author+year+venue** - Likely duplicate → warn user

## Required BibTeX Fields

### @article
- author, title, journal, year

### @inproceedings
- author, title, booktitle, year

### @book
- author/editor, title, publisher, year

### @misc (arXiv)
- author, title, year, eprint, archiveprefix

## Validation Checks

- [ ] Entry type is valid (@article, @inproceedings, etc.)
- [ ] Required fields present for entry type
- [ ] No unescaped special characters in fields
- [ ] Braces properly balanced
- [ ] Year is numeric
- [ ] Pages format correct (e.g., 123--145)

## Common Fixes Applied Automatically

- Convert `pages = {123-145}` → `pages = {123--145}`
- Escape special characters: `&` → `\&`
- Normalize author format: `Last, First and Last, First`
- Remove trailing commas in fields

## Error Handling

If validation fails:
```markdown
## Validation Error

**Issue**: Missing required field 'journal' for @article
**Entry**: SmithJones2024

**Suggested Fix**: Add journal field or change to @misc for preprints
```
