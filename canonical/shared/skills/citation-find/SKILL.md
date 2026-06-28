---
name: citation-find
description: >
  Search for academic sources with verified quote extraction to support claims.
  Use when: (1) user says "find papers for", "找文献支撑", "search references",
  "I need citations for", (2) revision requires new supporting evidence,
  (3) related work section needs expansion, (4) claim needs empirical backing.
  CRITICAL: Extracts exact supporting quotes from source fulltext to verify
  citation validity. Prioritizes Zotero library with web search fallback.
---

# Find Sources

Locate relevant academic sources AND extract verified supporting quotes.

## Core Principle: Quote-First Verification

Every recommended source MUST include an extracted quote that directly
supports the claim. If no supporting quote can be found in the fulltext,
the source should NOT be recommended.

## Process

1. Understand the claim/gap needing support
2. Formulate semantic search query
3. Search Zotero library first: `zotero_semantic_search`
4. For each candidate:
   - Retrieve fulltext: `zotero_get_item_fulltext`
   - Search for passages that directly support the claim
   - Extract 1-3 sentence quote with page/section reference
   - **If no supporting quote found → discard candidate**
5. Rank by quote strength and relevance
6. Present verified candidates with extracted quotes

## Output Format

### Claim to Support
> "{The exact claim from manuscript that needs citation}"

### Search Strategy
- **Primary query**: "{semantic query}"
- **Backup queries**: ["{alt1}", "{alt2}"]

---

### Source 1: Author (Year)
- **Citation**: Author, A., & Author, B. (Year). Title. *Journal*.
- **Relevance**: ⭐⭐⭐⭐⭐
- **Zotero Key**: `ABC123`

**Supporting Quote:**
> "Exact quote from the paper that supports the claim, typically 1-3 sentences
> that directly provide evidence for what you're trying to cite."
> — (Section X.X, Page Y)

**How to integrate**: Suggested phrasing for incorporating this citation

---

### Source 2: Author (Year)
[Same format]

---

### Sources Reviewed but Rejected
| Paper | Reason for Rejection |
|-------|---------------------|
| Smith (2023) | Fulltext unavailable in Zotero |
| Jones (2022) | Related topic but no direct support for this specific claim |

### Recommendation
[Which source(s) to use, in what order of preference, and why]

## Zotero Tools

```python
# 1. Semantic search
zotero_semantic_search(query="your query", limit=10)

# 2. Get metadata
zotero_get_item_metadata(item_key="ABC123", format="bibtex")

# 3. Get fulltext for quote extraction - CRITICAL
zotero_get_item_fulltext(item_key="ABC123")

# 4. Check existing annotations
zotero_get_annotations(item_key="ABC123")
```

## Quote Quality Criteria

### Good quotes (use these)
- Directly states or strongly implies the claim
- Contains specific evidence (numbers, findings, definitions)
- Self-contained and understandable without context
- From methods/results sections for empirical claims
- From introduction/related work for established facts

### Reject if
- Only mentions keywords without substantive support
- Requires heavy interpretation to connect to claim
- Quote is about a different aspect of the topic
- Source is tangentially related but doesn't support the specific claim

## Relevance Scoring

- ⭐⭐⭐⭐⭐ Quote directly states what you're claiming
- ⭐⭐⭐⭐ Quote strongly implies/supports the claim
- ⭐⭐⭐ Quote provides partial support, may need additional sources
- ⭐⭐ Weak connection, use only if nothing better
- ⭐ Do not recommend

## Fallback: Web Search

If Zotero results insufficient:
1. Use WebSearch for arXiv, Semantic Scholar
2. Note: Cannot extract quotes without fulltext access
3. Mark as "External Source - needs Zotero import for verification"

See [search-strategies.md](references/search-strategies.md) for query formulation tips.
