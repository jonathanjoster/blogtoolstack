import pytest

from validate_article import validate_article_text

VALID_ARTICLE = """---
title: "Kit vs Mailchimp for Bloggers"
description: "A comparison for bloggers choosing an email tool."
pubDate: 2026-09-13
format: comparison
targetKeyword: "kit vs mailchimp"
leadMagnet: true
---

Some intro text.

<AffiliateDisclosure />

More content with a call to action.

<KitSignupCTA />

<LeadMagnetOptIn />
"""


def test_valid_article_passes():
    result = validate_article_text(VALID_ARTICLE)
    assert result.ok
    assert result.errors == []


def test_missing_frontmatter_block_raises():
    with pytest.raises(ValueError):
        validate_article_text("just some text, no frontmatter")


def test_missing_required_field_fails():
    text = VALID_ARTICLE.replace('targetKeyword: "kit vs mailchimp"\n', "")
    result = validate_article_text(text)
    assert not result.ok
    assert any("targetKeyword" in e for e in result.errors)


def test_invalid_format_fails():
    text = VALID_ARTICLE.replace("format: comparison", "format: listicle-ish")
    result = validate_article_text(text)
    assert not result.ok
    assert any("invalid format" in e for e in result.errors)


def test_missing_disclosure_fails():
    text = VALID_ARTICLE.replace("<AffiliateDisclosure />\n\n", "")
    result = validate_article_text(text)
    assert not result.ok
    assert any("disclosure" in e for e in result.errors)


def test_missing_kit_cta_fails():
    text = VALID_ARTICLE.replace("<KitSignupCTA />\n\n", "")
    result = validate_article_text(text)
    assert not result.ok
    assert any("Kit signup CTA" in e for e in result.errors)


def test_lead_magnet_flag_without_component_fails():
    text = VALID_ARTICLE.replace("<LeadMagnetOptIn />\n", "")
    result = validate_article_text(text)
    assert not result.ok
    assert any("LeadMagnetOptIn" in e for e in result.errors)


def test_lead_magnet_false_does_not_require_component():
    text = VALID_ARTICLE.replace("leadMagnet: true", "leadMagnet: false").replace("\n<LeadMagnetOptIn />\n", "\n")
    result = validate_article_text(text)
    assert result.ok
