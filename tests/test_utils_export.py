import pytest
import io
import sys
from unittest.mock import patch
from marker.utils import export


class DummyTranslationString:
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return str(self.msg)

def dummy_(msg):
    return DummyTranslationString(msg)

@pytest.mark.parametrize("rows,header_row", [
    ([['A', 'B', 'C']], ['Col1', 'Col2', 'Col3']),
    ([['X', 'Y', 'Z']], ['Name', 'Role', 'Email']),
])
def test_response_xlsx_basic(rows, header_row):
    with patch.object(export, '_', dummy_):
        response = export.response_xlsx(rows, header_row)
        assert hasattr(response, 'body_file')
        assert hasattr(response, 'content_type')
        assert hasattr(response, 'content_disposition')
        assert response.content_type.startswith('application/vnd.openxmlformats-officedocument')
        assert 'attachment' in response.content_disposition
