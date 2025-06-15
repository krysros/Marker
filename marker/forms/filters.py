import re


def strip_filter(v):
    """Removes whitespace, newlines, and tabs from the beginning/end of a string."""
    return v.strip() if v else ""


def dash_filter(v):
    """Replace em dash, en dash, minus sign, hyphen-minus with a hypen"""
    return (
        v.replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u2212", "-")
        .replace("\u002d", "-")
    )


def remove_multiple_spaces(v):
    """Replaces multiple spaces with a single space."""
    return re.sub(" +", " ", v) if v else ""


def remove_dashes_and_spaces(v):
    """Removes dashes and spaces from a string."""
    return v.replace("-", "").replace(" ", "") if v else ""


def remove_mailto(v):
    """Removes "mailto:" from a string."""
    if v.startswith("mailto:"):
        return v[7:]
    else:
        return v


def title(v):
    """Return a titlecased version of the string."""
    return v.title()
