"""Column list helpers for export dropdowns in Mako templates.

Each function accepts the Pyramid translate callable ``_`` and returns a list
of translated column-name strings that match the header_row produced by the
corresponding ``_*_export_header`` method in the view.

Usage in a Mako template::

    <%! from marker.utils.export_columns import company_cols, project_cols %>
    <% _export_cols = company_cols(_) %>
"""


def contact_cols(_):
    return [
        _("Contact name"),
        _("Contact role"),
        _("Contact phone"),
        _("Contact email"),
    ]


def company_cols(_):
    return contact_cols(_) + [
        _("Company name"),
        _("Company street"),
        _("Company post code"),
        _("Company city"),
        _("Company subdivision"),
        _("Company country"),
        _("Company website"),
        _("Company NIP"),
        _("Company REGON"),
        _("Company KRS"),
        _("Tags"),
    ]


def project_cols(_):
    return contact_cols(_) + [
        _("Project name"),
        _("Project street"),
        _("Project post code"),
        _("Project city"),
        _("Project subdivision"),
        _("Project country"),
        _("Project website"),
        _("Project deadline"),
        _("Project stage"),
        _("Project delivery method"),
        _("Project object category"),
        _("Tags"),
    ]


def tag_company_cols(_):
    """Column list for tag-scoped company exports (Tag inserted after contact cols)."""
    return contact_cols(_) + [_("Tag")] + company_cols(_)[4:]


def tag_project_cols(_):
    """Column list for tag-scoped project exports (Tag inserted after contact cols)."""
    return contact_cols(_) + [_("Tag")] + project_cols(_)[4:]


def prices_cols(_):
    return [
        _("Project"),
        _("Object category"),
        _("Company"),
        _("Stage"),
        _("Role"),
        _("Currency"),
        _("Net value"),
        _("Gross value"),
        _("Net / m\u00b2"),
        _("Gross / m\u00b2"),
    ]
