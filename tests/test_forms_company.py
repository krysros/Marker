"""Tests for marker/forms/company.py checksum functions."""

from marker.forms.company import _check_sum_9, _check_sum_14


def test_check_sum_9_with_modulo_10():
    """Cover line 25: check_sum == 10 maps to 0, digits[8] == 0 → True."""
    # 8*1 + 9*0 + 2*5 + 3*1 + 4*1 + 5*1 + 6*1 + 7*1 = 43, 43 % 11 = 10 → 0
    digits = [1, 0, 5, 1, 1, 1, 1, 1, 0]
    assert _check_sum_9(digits) is True


def test_check_sum_14_with_modulo_10():
    """Cover line 36: check_sum == 10 maps to 0, digits[13] == 0 → True."""
    digits = [1, 0, 5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0]
    assert _check_sum_14(digits) is True


def test_check_sum_14_mismatch():
    """Cover line 40: check_sum != digits[13] → False."""
    # check_sum = 4, digits[13] = 0 → mismatch
    digits = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0]
    assert _check_sum_14(digits) is False
