"""Tests for marker/views/subdivision.py"""

from unittest.mock import MagicMock

from webob.multidict import MultiDict

import marker.forms.ts
from marker.views.subdivision import subdivision_view


def test_subdivision_view():
    request = MagicMock()
    request.params = MultiDict({"country": "PL"})
    result = subdivision_view(request)
    assert "subdivisions" in result
    assert isinstance(result["subdivisions"], list)


def test_subdivision_view_no_country():
    request = MagicMock()
    request.params = MultiDict()
    result = subdivision_view(request)
    assert "subdivisions" in result
