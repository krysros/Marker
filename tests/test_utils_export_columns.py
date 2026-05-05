from marker.utils import export_columns


def _identity_translate(value):
    return value


def test_contact_company_project_columns_shape():
    contact = export_columns.contact_cols(_identity_translate)
    company = export_columns.company_cols(_identity_translate)
    project = export_columns.project_cols(_identity_translate)

    assert len(contact) == 4
    assert company[:4] == contact
    assert project[:4] == contact


def test_tag_company_cols_inserts_tag_after_contact_prefix():
    cols = export_columns.tag_company_cols(_identity_translate)
    assert cols[4] == "Tag"
    assert "Company name" in cols


def test_tag_project_cols_inserts_tag_after_contact_prefix():
    cols = export_columns.tag_project_cols(_identity_translate)
    assert cols[4] == "Tag"
    assert "Project name" in cols


def test_prices_cols_contains_density_columns():
    cols = export_columns.prices_cols(_identity_translate)
    assert "Net / m²" in cols
    assert "Gross / m²" in cols
