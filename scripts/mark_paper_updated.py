from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPERS = ROOT / "data" / "papers.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Update a paper's updated date in data/papers.json.")
    parser.add_argument("slug", help="Paper slug from data/papers.json")
    parser.add_argument("--date", default=date.today().isoformat(), help="Date in YYYY-MM-DD format")
    args = parser.parse_args()

    papers = json.loads(PAPERS.read_text(encoding="utf-8"))
    for paper in papers:
        if paper["slug"] == args.slug:
            paper["updated"] = args.date
            break
    else:
        raise SystemExit(f"No paper found with slug: {args.slug}")

    PAPERS.write_text(json.dumps(papers, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {args.slug} to {args.date}")


if __name__ == "__main__":
    main()
