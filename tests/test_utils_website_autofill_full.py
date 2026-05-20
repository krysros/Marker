
import pytest
import types
import unicodedata
from marker.utils import website_autofill

def test_subdivision_code_from_value_empty():
	assert website_autofill._subdivision_code_from_value("", "PL") == ""
	assert website_autofill._subdivision_code_from_value("Mazowieckie", "") == ""

def test_normalize_whitespace():
	assert website_autofill._normalize_whitespace("  a  b   c ") == "a b c"

def test_fold_text():
	s = "łódź ß đ ø"
	folded = website_autofill._fold_text(s)
	assert "l" in folded and "ss" in folded and "d" in folded and "o" in folded
	# Should remove diacritics
	assert "ł" not in folded and "ß" not in folded

def test_valueerror_on_content_parts(monkeypatch):
	# Coverage: ValueError when content cannot be retrieved
	monkeypatch.setattr(website_autofill, "WebBaseLoader", lambda url: types.SimpleNamespace(load=lambda: []))
	with pytest.raises(ValueError):
		website_autofill._autofill_from_website("http://example.com", "prompt")
