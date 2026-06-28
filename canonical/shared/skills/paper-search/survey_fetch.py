#!/usr/bin/env python3
"""
survey_fetch.py — Batch fetch arXiv papers for a given time range and keywords.

Handles large time ranges (weeks to months) by paginating arXiv API requests.
Uses the same scoring logic as daily-papers but with custom keyword override support.

Usage:
    python3 survey_fetch.py --months 3 --keywords "world model,embodied ai" --categories "cs.RO,cs.CV"
    python3 survey_fetch.py --days 30 --keywords "diffusion policy,robot learning"
    python3 survey_fetch.py --months 2  # uses default keywords from user-config.json

Output: JSON array to stdout, progress to stderr.
"""

import argparse
import json
import math
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

_SHARED_DIR = Path(__file__).resolve().parent.parent / "_shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

from user_config import daily_papers_config

_CONFIG = daily_papers_config()

ATOM_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}


def fetch_url(url: str, timeout: int = 60, max_retries: int = 5) -> str:
    for attempt in range(max_retries):
        try:
            req = Request(url, headers={"User-Agent": "paper-survey-bot/1.0"})
            with urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "SSL" in err_str or "EOF" in err_str:
                wait = 10 * (attempt + 1)
                print(f"  [RETRY {attempt+1}/{max_retries}] {e}, waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
            else:
                print(f"  [WARN] fetch failed: {e}", file=sys.stderr)
                return ""
    print(f"  [WARN] all {max_retries} retries exhausted", file=sys.stderr)
    return ""


# ── Auto-tagging rules ──────────────────────────────────────────────
# Two dimensions:
#   genre:  what TYPE of paper (method, benchmark, survey, framework, analysis)
#   topic:  what CONTENT the paper covers (detected via keyword matching)
#
# Genre rules use title + abstract heuristics.
# Topic rules are keyword-based and can be extended per-survey via --tag-rules.

GENRE_RULES: list[tuple[str, list[str], list[str]]] = [
    # (tag, title_patterns, abstract_patterns)
    ("type:benchmark", ["benchmark", "dataset", "evaluation suite"],
     ["we introduce a benchmark", "we propose a benchmark", "evaluation benchmark",
      "we present a dataset", "new dataset", "test suite"]),
    ("type:survey", ["survey", "review", "systematic review", "overview"],
     ["we survey", "comprehensive review", "literature review", "we review"]),
    ("type:framework", ["framework", "system", "platform", "toolkit"],
     ["we propose a framework", "we present a system", "our framework",
      "we design a framework", "system architecture"]),
    ("type:analysis", ["analysis", "empirical study", "study of", "investigation"],
     ["empirical analysis", "we analyze", "we investigate", "ablation study",
      "comparative study"]),
    # method is the default fallback — assigned if no other genre matched
]

TOPIC_RULES: dict[str, list[str]] = {
    "topic:RL":             ["reinforcement learning", "reward model", "rlhf",
                             "policy gradient", "ppo", "dpo", "reward shaping"],
    "topic:multiagent":     ["multi-agent", "multiagent", "multi agent",
                             "agent collaboration", "agent communication",
                             "cooperative agent", "agent society"],
    "topic:embodied":       ["embodied", "robot", "manipulation", "navigation",
                             "locomotion", "sim-to-real", "sim2real"],
    "topic:personalization":["personalization", "personalized", "personal preference",
                             "user preference", "user modeling", "user profile",
                             "personal information", "user adaptation"],
    "topic:memory":         ["memory system", "memory architecture", "memory mechanism",
                             "long-term memory", "episodic memory", "memory retrieval",
                             "memory management", "working memory", "memory module"],
    "topic:self-evolving":  ["self-evolving", "self-improving", "continual learning",
                             "lifelong learning", "skill acquisition", "skill learning",
                             "self-reflection", "self-refinement"],
    "topic:LLM-agent":     ["llm agent", "language agent", "llm-based agent",
                             "agent framework", "tool use", "function calling",
                             "agentic"],
    "topic:RAG":           ["retrieval augmented", "retrieval-augmented", "rag",
                             "knowledge retrieval", "external knowledge"],
    "topic:conversation":  ["dialogue", "conversational", "chat", "conversation",
                             "dialogue history", "multi-turn"],
}


def generate_tags(paper: dict, extra_topic_rules: dict | None = None) -> list[str]:
    """Auto-generate tags for a paper based on title + abstract content."""
    text = (paper["title"] + " " + paper["abstract"]).lower()
    title_lower = paper["title"].lower()
    tags: list[str] = []

    # ── Genre detection ──
    genre_found = False
    for tag, title_pats, abstract_pats in GENRE_RULES:
        if any(p in title_lower for p in title_pats) or any(p in text for p in abstract_pats):
            tags.append(tag)
            genre_found = True
            break  # one genre per paper
    if not genre_found:
        tags.append("type:method")

    # ── Topic detection ──
    all_rules = dict(TOPIC_RULES)
    if extra_topic_rules:
        all_rules.update(extra_topic_rules)

    for tag, patterns in all_rules.items():
        if any(p in text for p in patterns):
            tags.append(tag)

    return tags


def score_paper(paper: dict, keywords: list[str], negative_keywords: list[str],
                domain_boost_keywords: list[str]) -> int:
    text = (paper["title"] + " " + paper["abstract"]).lower()
    title_lower = paper["title"].lower()

    for neg in negative_keywords:
        if neg.lower() in text:
            return -999

    score = 0

    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in title_lower:
            score += 3
        elif kw_lower in text:
            score += 1

    domain_hits = sum(1 for kw in domain_boost_keywords if kw.lower() in text)
    if domain_hits >= 2:
        score += 2
    elif domain_hits == 1:
        score += 1

    return score


def fetch_arxiv_batch(categories: list[str], start: int, max_results: int,
                      timeout: int = 90) -> str:
    cats = "+OR+".join(f"cat:{c}" for c in categories)
    url = (
        f"https://export.arxiv.org/api/query?"
        f"search_query=({cats})"
        f"&sortBy=submittedDate&sortOrder=descending"
        f"&start={start}&max_results={max_results}"
    )
    return fetch_url(url, timeout=timeout)


def parse_arxiv_entries(xml_text: str, start_date, end_date) -> list[dict]:
    if not xml_text:
        return []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"  [WARN] XML parse error: {e}", file=sys.stderr)
        return []

    papers = []
    for entry in root.findall("atom:entry", ATOM_NS):
        title_el = entry.find("atom:title", ATOM_NS)
        summary_el = entry.find("atom:summary", ATOM_NS)
        published_el = entry.find("atom:published", ATOM_NS)
        id_el = entry.find("atom:id", ATOM_NS)

        if title_el is None or summary_el is None:
            continue

        title = " ".join(title_el.text.split())
        abstract = " ".join(summary_el.text.split())
        entry_url = id_el.text.strip() if id_el is not None else ""
        date = published_el.text[:10] if published_el is not None else ""

        # Date filter
        if date:
            try:
                pub_date = datetime.strptime(date, "%Y-%m-%d").date()
                if pub_date < start_date or pub_date > end_date:
                    continue
            except ValueError:
                pass

        arxiv_id = entry_url.split("/abs/")[-1] if "/abs/" in entry_url else ""

        author_els = entry.findall("atom:author", ATOM_NS)
        names = []
        affiliations = set()
        for a in author_els:
            name_el = a.find("atom:name", ATOM_NS)
            if name_el is not None and name_el.text:
                names.append(name_el.text.strip())
            for aff_el in a.findall("arxiv:affiliation", ATOM_NS):
                if aff_el.text and aff_el.text.strip():
                    affiliations.add(aff_el.text.strip())

        cat_el = entry.find("arxiv:primary_category", ATOM_NS)
        category = cat_el.get("term", "") if cat_el is not None else ""

        papers.append({
            "title": title,
            "authors": ", ".join(names),
            "affiliations": ", ".join(sorted(affiliations)) if affiliations else "",
            "abstract": abstract,
            "url": entry_url,
            "pdf": f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else "",
            "date": date,
            "score": 0,
            "category": category,
            "source": "arxiv",
        })

    return papers


def main():
    parser = argparse.ArgumentParser(description="Batch fetch arXiv papers for survey")
    parser.add_argument("--days", type=int, default=0, help="Number of days to look back")
    parser.add_argument("--months", type=int, default=0, help="Number of months to look back")
    parser.add_argument("--keywords", type=str, default="",
                        help="Comma-separated keywords (overrides config)")
    parser.add_argument("--negative-keywords", type=str, default="",
                        help="Comma-separated negative keywords (overrides config)")
    parser.add_argument("--categories", type=str, default="",
                        help="Comma-separated arXiv categories (overrides config)")
    parser.add_argument("--min-score", type=int, default=None,
                        help="Minimum score threshold (default: from config)")
    parser.add_argument("--top-n", type=int, default=100,
                        help="Max number of papers to return (default: 100)")
    parser.add_argument("--output", type=str, default="",
                        help="Output file path (default: stdout)")
    args = parser.parse_args()

    # Resolve time range
    if args.months > 0:
        days = args.months * 30
    elif args.days > 0:
        days = args.days
    else:
        print("Error: specify --days or --months", file=sys.stderr)
        sys.exit(1)

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    # Resolve keywords
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()] if args.keywords else _CONFIG["keywords"]
    negative_keywords = ([k.strip() for k in args.negative_keywords.split(",") if k.strip()]
                         if args.negative_keywords else _CONFIG["negative_keywords"])
    domain_boost = _CONFIG["domain_boost_keywords"]
    categories = [c.strip() for c in args.categories.split(",") if c.strip()] if args.categories else _CONFIG["arxiv_categories"]
    min_score = args.min_score if args.min_score is not None else _CONFIG["min_score"]

    print(f"[survey_fetch] Range: {start_date} ~ {end_date} ({days} days)", file=sys.stderr)
    print(f"[survey_fetch] Keywords: {keywords}", file=sys.stderr)
    print(f"[survey_fetch] Categories: {categories}", file=sys.stderr)
    print(f"[survey_fetch] Min score: {min_score}, Top N: {args.top_n}", file=sys.stderr)

    # Paginate arXiv API (max 2000 per request, 3s delay between)
    PAGE_SIZE = 2000
    # Estimate: ~400 papers/day across cs.RO+cs.CV+cs.AI+cs.LG
    estimated_total = days * 400
    num_pages = min(math.ceil(estimated_total / PAGE_SIZE), 25)  # cap at 50k papers

    all_papers = []
    seen_ids = set()

    for page in range(num_pages):
        offset = page * PAGE_SIZE
        print(f"  Fetching page {page + 1}/{num_pages} (offset={offset})...", file=sys.stderr)

        xml_text = fetch_arxiv_batch(categories, offset, PAGE_SIZE)
        if not xml_text:
            print(f"  [WARN] Empty response at page {page + 1}, stopping", file=sys.stderr)
            break

        papers = parse_arxiv_entries(xml_text, start_date, end_date)
        print(f"  Got {len(papers)} papers in date range", file=sys.stderr)

        if not papers and page > 0:
            # No more papers in range
            break

        for p in papers:
            aid = re.search(r"(\d{4}\.\d{4,5})", p["url"])
            if aid:
                aid = aid.group(1)
                if aid not in seen_ids:
                    seen_ids.add(aid)
                    all_papers.append(p)

        # Respect arXiv rate limit
        if page < num_pages - 1:
            print(f"  Waiting 3s (arXiv rate limit)...", file=sys.stderr)
            time.sleep(3)

    print(f"\n[survey_fetch] Total unique papers fetched: {len(all_papers)}", file=sys.stderr)

    # Score, tag, and filter
    scored = []
    for p in all_papers:
        p["score"] = score_paper(p, keywords, negative_keywords, domain_boost)
        p["tags"] = generate_tags(p)
        if p["score"] >= min_score:
            scored.append(p)

    scored.sort(key=lambda x: (-x["score"], x["date"]))
    top = scored[:args.top_n]

    print(f"[survey_fetch] After scoring: {len(scored)} >= min_score, returning top {len(top)}", file=sys.stderr)

    # Output
    output = json.dumps(top, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output + "\n")
        print(f"[survey_fetch] Saved to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
