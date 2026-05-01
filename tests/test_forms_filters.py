"""Tests for marker/forms/filters.py"""

from marker.forms.filters import remove_mailto, remove_pl_prefix


def test_remove_mailto_with_prefix():
    assert remove_mailto("mailto:test@example.com") == "test@example.com"


def test_remove_pl_prefix_strips_pl():
    assert remove_pl_prefix("PL1234567890") == "1234567890"
    assert remove_pl_prefix("pl1234567890") == "1234567890"
    # leading/trailing whitespace stripped from v, but not from the part after PL
    assert remove_pl_prefix(" PL 1234") == " 1234"


def test_remove_pl_prefix_no_prefix():
    assert remove_pl_prefix("1234567890") == "1234567890"
    assert remove_pl_prefix(None) is None
    assert remove_pl_prefix("") == ""
