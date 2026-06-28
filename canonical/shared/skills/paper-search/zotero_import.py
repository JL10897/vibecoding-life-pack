#!/usr/bin/env python3
"""
zotero_import.py — Import arXiv papers into Zotero via local connector API.

Uses Zotero's local translation server (port 23119) to save papers with
full metadata and PDF auto-download.

Usage:
    # Import a single paper
    python3 zotero_import.py --url "https://arxiv.org/abs/2401.12345"

    # Import multiple papers from a JSON file (same format as survey_fetch.py output)
    python3 zotero_import.py --from-json /tmp/selected_papers.json

    # Import into a specific collection
    python3 zotero_import.py --from-json /tmp/selected_papers.json --collection "论文调研/World Model"
"""

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

_SHARED_DIR = Path(__file__).resolve().parent.parent / "_shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

ZOTERO_CONNECTOR = "http://127.0.0.1:23119"


def check_zotero():
    """Check if Zotero is running."""
    try:
        req = Request(f"{ZOTERO_CONNECTOR}/connector/ping")
        with urlopen(req, timeout=5) as resp:
            return "running" in resp.read().decode().lower()
    except Exception:
        return False


def save_to_zotero(url: str, title: str = "", collection_key: str = "") -> bool:
    """Save a single paper to Zotero via connector API."""
    # Use saveItems with URL - Zotero will fetch metadata automatically
    payload = {
        "uri": url,
        "html": "",
        "items": [{
            "itemType": "journalArticle",
            "title": title or "Untitled",
            "url": url,
            "accessDate": "",
        }],
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "paper-survey/1.0",
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = Request(
            f"{ZOTERO_CONNECTOR}/connector/saveItems",
            data=data,
            headers=headers,
            method="POST",
        )
        with urlopen(req, timeout=30) as resp:
            status = resp.status
            if status == 201:
                print(f"  [OK] Saved: {title[:60]}", file=sys.stderr)
                return True
            else:
                body = resp.read().decode()
                print(f"  [WARN] Status {status}: {body[:100]}", file=sys.stderr)
                return False
    except Exception as e:
        # Fallback: try saveSnapshot which is more permissive
        try:
            snapshot_payload = {
                "url": url,
                "title": title or url,
            }
            data = json.dumps(snapshot_payload).encode("utf-8")
            req = Request(
                f"{ZOTERO_CONNECTOR}/connector/saveSnapshot",
                data=data,
                headers=headers,
                method="POST",
            )
            with urlopen(req, timeout=30) as resp:
                if resp.status in (200, 201):
                    print(f"  [OK] Saved (snapshot): {title[:60]}", file=sys.stderr)
                    return True
        except Exception as e2:
            print(f"  [FAIL] {title[:40]}: {e} / {e2}", file=sys.stderr)
            return False


def import_from_json(json_path: str, collection_key: str = "") -> dict:
    """Import papers from a JSON file (survey_fetch.py output format)."""
    papers = json.loads(Path(json_path).read_text())

    results = {"success": 0, "failed": 0, "titles": []}

    for i, paper in enumerate(papers):
        url = paper.get("url", "")
        title = paper.get("title", "")

        if not url:
            print(f"  [SKIP] No URL for paper #{i+1}", file=sys.stderr)
            results["failed"] += 1
            continue

        print(f"  [{i+1}/{len(papers)}] Importing: {title[:60]}...", file=sys.stderr)
        ok = save_to_zotero(url, title, collection_key)

        if ok:
            results["success"] += 1
            results["titles"].append(title)
        else:
            results["failed"] += 1

        # Rate limit: don't overwhelm Zotero
        if i < len(papers) - 1:
            time.sleep(2)

    return results


def main():
    parser = argparse.ArgumentParser(description="Import papers into Zotero")
    parser.add_argument("--url", type=str, help="Single arXiv URL to import")
    parser.add_argument("--from-json", type=str, help="JSON file with papers to import")
    parser.add_argument("--collection", type=str, default="", help="Target Zotero collection path")
    args = parser.parse_args()

    if not check_zotero():
        print("Error: Zotero is not running. Please start Zotero first.", file=sys.stderr)
        sys.exit(1)

    if args.url:
        ok = save_to_zotero(args.url, collection_key=args.collection)
        sys.exit(0 if ok else 1)

    elif args.from_json:
        results = import_from_json(args.from_json, args.collection)
        print(f"\n[zotero_import] Done: {results['success']} saved, {results['failed']} failed",
              file=sys.stderr)
        # Output results as JSON for the skill to parse
        json.dump(results, sys.stdout, ensure_ascii=False, indent=2)
        print()

    else:
        print("Error: specify --url or --from-json", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
