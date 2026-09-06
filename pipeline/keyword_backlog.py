#!/usr/bin/env python3
"""Keyword backlog manager for the BlogToolStack Pinterest content pipeline.

Stores parent keywords (with child keywords, search volume, competition,
and reference pin URLs) collected manually from Pinterest's free tools
(Trends, search-suggestion autocomplete, ad-account keyword volume) into
a structured JSON backlog, so the weekly content batch can pull the next
topic without re-doing the research by hand each time.
"""
import argparse
import json
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

BACKLOG_PATH = Path(__file__).resolve().parent.parent / "content-backlog" / "keywords.json"

COMPETITION_WEIGHT = {"low": 3, "medium": 2, "high": 1}


@dataclass
class KeywordEntry:
    parent_keyword: str
    search_volume: Optional[int] = None
    competition: Optional[str] = None
    child_keywords: list = field(default_factory=list)
    source_pin_urls: list = field(default_factory=list)
    status: str = "backlog"
    added_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def priority_score(self) -> float:
        if self.search_volume is None or self.competition is None:
            return 0.0
        weight = COMPETITION_WEIGHT.get(self.competition, 1)
        return self.search_volume * weight


def load_backlog(path: Path = BACKLOG_PATH):
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [KeywordEntry(**item) for item in raw]


def save_backlog(entries, path: Path = BACKLOG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([asdict(e) for e in entries], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def add_entry(entries, **kwargs):
    for e in entries:
        if e.parent_keyword == kwargs["parent_keyword"]:
            raise ValueError(f"keyword already in backlog: {kwargs['parent_keyword']}")
    entries.append(KeywordEntry(**kwargs))
    return entries


def set_status(entries, parent_keyword: str, status: str):
    for e in entries:
        if e.parent_keyword == parent_keyword:
            e.status = status
            return entries
    raise ValueError(f"keyword not found: {parent_keyword}")


def sorted_by_priority(entries, status: Optional[str] = None):
    filtered = [e for e in entries if status is None or e.status == status]
    return sorted(filtered, key=lambda e: e.priority_score(), reverse=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage the Pinterest keyword backlog")
    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="add a parent keyword to the backlog")
    add_p.add_argument("--keyword", required=True)
    add_p.add_argument("--search-volume", type=int, default=None)
    add_p.add_argument("--competition", choices=["low", "medium", "high"], default=None)
    add_p.add_argument("--child-keywords", default="")
    add_p.add_argument("--source-pins", default="")

    list_p = sub.add_parser("list", help="list backlog entries by priority")
    list_p.add_argument("--status", choices=["backlog", "in_progress", "published"], default=None)

    status_p = sub.add_parser("set-status", help="update a keyword status")
    status_p.add_argument("--keyword", required=True)
    status_p.add_argument("--status", required=True, choices=["backlog", "in_progress", "published"])

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    entries = load_backlog()

    if args.command == "add":
        child_keywords = [k.strip() for k in args.child_keywords.split(",") if k.strip()]
        source_pins = [u.strip() for u in args.source_pins.split(",") if u.strip()]
        try:
            entries = add_entry(
                entries,
                parent_keyword=args.keyword,
                search_volume=args.search_volume,
                competition=args.competition,
                child_keywords=child_keywords,
                source_pin_urls=source_pins,
            )
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        save_backlog(entries)
        print(f"added: {args.keyword}")
        return 0

    if args.command == "list":
        for e in sorted_by_priority(entries, status=args.status):
            print(f"{e.priority_score():>10.1f}  {e.parent_keyword}  [{e.status}]  vol={e.search_volume} comp={e.competition}")
        return 0

    if args.command == "set-status":
        try:
            entries = set_status(entries, args.keyword, args.status)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        save_backlog(entries)
        print(f"updated: {args.keyword} -> {args.status}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
