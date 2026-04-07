"""Tests for marker/forms/filters.py"""

from marker.forms.filters import remove_mailto


def test_remove_mailto_with_prefix():
    assert remove_mailto("mailto:test@example.com") == "test@example.com"
