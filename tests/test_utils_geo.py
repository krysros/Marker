
from marker.utils.geo import _first_not_empty


def test_first_not_empty_returns_first_nonempty():
    assert _first_not_empty(None, "", "  ", "foo", "bar") == "foo"
    assert _first_not_empty("", None, "bar") == "bar"
    assert _first_not_empty("baz", "", None) == "baz"
    assert _first_not_empty(None, "", "   ") == ""
