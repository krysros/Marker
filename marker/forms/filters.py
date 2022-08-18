import re


def strip_filter(v):
    """Removes whitespace, newlines, and tabs from the beginning/end of a string."""
    return v.strip() if v else ''


def dash_filter(v):
    """Replace em dash, en dash, minus sign, hyphen-minus with a hypen"""
    return v.replace("\u2014", "-").replace("\u2013", "-").replace("\u2212", "-").replace("\u002D", "-")


def remove_multiple_spaces(v):
    """Replaces multiple spaces with a single space."""
    return re.sub(" +", " ", v) if v else ''


def remove_dashes_and_spaces(v):
    """Removes dashes and spaces from a string."""
    return v.replace("-", "").replace(" ", "") if v else ''


def remove_mailto(v):
    """Removes "mailto:" from a string."""
    if v.startswith("mailto:"):
        return v[7:]
    else:
        return v


def extract_postcode_and_city(v):
    # Remove spaces at the beginning and at the end of the string
    v = v.strip()
    # Replace em dash, en dash, minus sign, hyphen-minus with a hypen
    v = dash_filter(v)
    # Extract postcode and city
    p = re.compile(r"\d{2}\s*-\s*\d{3}")
    postcode = p.findall(v)
    if postcode:
        postcode = postcode[0]
        city = v.replace(postcode, "").strip()
        postcode = postcode.replace("\t", "").replace(" ", "")
    else:
        postcode = ""
    return postcode, city