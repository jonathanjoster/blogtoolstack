import pytest

from keyword_backlog import (
    KeywordEntry,
    add_entry,
    load_backlog,
    save_backlog,
    set_status,
    sorted_by_priority,
)


def test_add_entry_appends_new_keyword():
    entries = []
    entries = add_entry(entries, parent_keyword="email marketing for bloggers", search_volume=1000, competition="low")
    assert len(entries) == 1
    assert entries[0].parent_keyword == "email marketing for bloggers"


def test_add_entry_rejects_duplicate():
    entries = [KeywordEntry(parent_keyword="kit vs mailchimp")]
    with pytest.raises(ValueError):
        add_entry(entries, parent_keyword="kit vs mailchimp")


def test_priority_score_favors_low_competition():
    high_comp = KeywordEntry(parent_keyword="a", search_volume=1000, competition="high")
    low_comp = KeywordEntry(parent_keyword="b", search_volume=1000, competition="low")
    assert low_comp.priority_score() > high_comp.priority_score()


def test_priority_score_zero_when_missing_data():
    entry = KeywordEntry(parent_keyword="c")
    assert entry.priority_score() == 0.0


def test_sorted_by_priority_orders_descending():
    entries = [
        KeywordEntry(parent_keyword="low", search_volume=100, competition="high"),
        KeywordEntry(parent_keyword="high", search_volume=1000, competition="low"),
    ]
    result = sorted_by_priority(entries)
    assert [e.parent_keyword for e in result] == ["high", "low"]


def test_sorted_by_priority_filters_by_status():
    entries = [
        KeywordEntry(parent_keyword="a", search_volume=100, competition="low", status="published"),
        KeywordEntry(parent_keyword="b", search_volume=100, competition="low", status="backlog"),
    ]
    result = sorted_by_priority(entries, status="backlog")
    assert [e.parent_keyword for e in result] == ["b"]


def test_set_status_updates_matching_entry():
    entries = [KeywordEntry(parent_keyword="kit vs mailchimp", status="backlog")]
    entries = set_status(entries, "kit vs mailchimp", "in_progress")
    assert entries[0].status == "in_progress"


def test_set_status_raises_for_unknown_keyword():
    with pytest.raises(ValueError):
        set_status([], "nonexistent", "in_progress")


def test_save_and_load_backlog_roundtrip(tmp_path):
    path = tmp_path / "keywords.json"
    entries = [KeywordEntry(parent_keyword="kit review", search_volume=500, competition="medium", child_keywords=["kit review 2026"])]
    save_backlog(entries, path=path)
    loaded = load_backlog(path=path)
    assert len(loaded) == 1
    assert loaded[0].parent_keyword == "kit review"
    assert loaded[0].child_keywords == ["kit review 2026"]
