#!/usr/bin/env python3
"""Validate a BlogToolStack article file against the required article
contract (see pipeline/article-template.md) before it can be published."""
import re
import sys
from pathlib import Path
from typing import NamedTuple

import yaml

REQUIRED_FRONTMATTER_FIELDS = ["title", "description", "pubDate", "format", "targetKeyword"]
VALID_FORMATS = {"comparison", "review", "how-to", "listicle"}

DISCLOSURE_MARKER = "<AffiliateDisclosure"
KIT_CTA_MARKER = "<KitSignupCTA"
LEAD_MAGNET_MARKER = "<LeadMagnetOptIn"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


class ValidationResult(NamedTuple):
    ok: bool
    errors: list


def parse_article(text: str):
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("article is missing --- frontmatter block")
    frontmatter = yaml.safe_load(match.group(1)) or {}
    body = match.group(2)
    return frontmatter, body


def validate_frontmatter(frontmatter: dict):
    errors = []
    for field_name in REQUIRED_FRONTMATTER_FIELDS:
        if not frontmatter.get(field_name):
            errors.append(f"missing frontmatter field: {field_name}")
    fmt = frontmatter.get("format")
    if fmt and fmt not in VALID_FORMATS:
        errors.append(f"invalid format '{fmt}', must be one of {sorted(VALID_FORMATS)}")
    return errors


def validate_body(frontmatter: dict, body: str):
    errors = []
    if DISCLOSURE_MARKER not in body:
        errors.append("missing affiliate disclosure block (<AffiliateDisclosure />)")
    if KIT_CTA_MARKER not in body:
        errors.append("missing Kit signup CTA (<KitSignupCTA />)")
    if frontmatter.get("leadMagnet") and LEAD_MAGNET_MARKER not in body:
        errors.append("frontmatter sets leadMagnet: true but body has no <LeadMagnetOptIn />")
    return errors


def validate_article_text(text: str) -> ValidationResult:
    frontmatter, body = parse_article(text)
    errors = validate_frontmatter(frontmatter) + validate_body(frontmatter, body)
    return ValidationResult(ok=not errors, errors=errors)


def validate_file(path: Path) -> ValidationResult:
    return validate_article_text(path.read_text(encoding="utf-8"))


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    if not argv:
        print("usage: validate_article.py <file.md> [file2.md ...]", file=sys.stderr)
        return 2
    exit_code = 0
    for arg in argv:
        result = validate_file(Path(arg))
        if result.ok:
            print(f"OK  {arg}")
        else:
            exit_code = 1
            print(f"FAIL {arg}")
            for err in result.errors:
                print(f"  - {err}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
