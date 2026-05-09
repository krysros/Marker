# AI Instructions for the Marker Project

## Project Overview

**Marker** is a Python web application built with:
- **Pyramid** (WSGI framework, `marker/__init__.py`)
- **SQLAlchemy** (ORM, models in `marker/models/`)
- **Alembic** (database migrations, `marker/alembic/`)
- **Mako** (templates, `marker/templates/`)
- **WTForms** (forms, `marker/forms/`)
- **Babel** (i18n, `marker/locale/`, languages: `en`, `pl`)
- **SQLite** for development (`sqlite:///marker.sqlite`)

Core entities: `User`, `Company`, `Project`, `Contact`, `Tag`, `Comment`, `Activity`.

Association tables (many-to-many): `companies_tags`, `projects_tags`, `companies_stars`, `projects_stars`, `selected_companies`, `selected_projects`, `selected_tags`, `selected_contacts`.

---

## Language Policy

- All source code, comments, docstrings, commit messages, and test code **must be in English**.
- User-facing strings use `request.translate(_("..."))` and are extracted via Babel.
- Polish translation is the only active non-English locale (`pl`).

---

## Project Layout

```
marker/
  __init__.py          # Pyramid app factory (main)
  models/              # SQLAlchemy ORM models (Base in meta.py)
  views/               # View classes and functions
    __init__.py        # Shared helpers: safe_redirect_target, update_selected_items, etc.
  forms/               # WTForms form definitions
  utils/               # Utilities: export.py, geo.py, website_autofill.py, contact_csv_import.py
  alembic/
    env.py             # Alembic env (reads settings from .ini)
    versions/          # One file per migration revision
  templates/           # Mako templates grouped by entity
  locale/              # Babel .pot/.po/.mo files
  routes.py            # All route definitions
  factories.py         # Pyramid traversal factories
  resources.py         # ACL resource classes
  security.py          # Auth policy (argon2, AuthTkt)
  security_settings.py # Secret/cookie setting helpers
  subscribers.py       # BeforeRender / NewRequest subscribers
  scripts/             # initialize_db script
tests/
  conftest.py          # Fixtures: dbengine, dbsession, testapp, app_request
  test_*.py            # One test file per module
```

---

## Development Commands

```bash
# Install dependencies
uv sync

# Run development server
uv run pserve development.ini

# Run tests
uv run pytest

# Run tests with coverage (must reach 100%)
uv run pytest --cov=marker --cov-report=term-missing

# Format code (run after every code change)
uv run isort .
uv run black .

# Alembic migrations
uv run alembic -c development.ini revision --autogenerate -m "description"
uv run alembic -c development.ini upgrade head
uv run alembic -c development.ini current
uv run alembic -c development.ini history

# i18n — extract, update, compile
uv run pybabel extract -F babel.cfg -o marker/locale/messages.pot .
uv run pybabel update -i marker/locale/messages.pot -d marker/locale
# Remove `fuzzy` flags from .po files, then:
uv run pybabel compile -d marker/locale
```

---

## Coding Conventions

### Models

- Inherit from `Base` (`marker.models.meta`).
- Use SQLAlchemy naming convention defined in `meta.py` (`NAMING_CONVENTION`).
- Foreign keys: `ondelete="CASCADE"` for ownership relations, `ondelete="SET NULL"` for soft references (`creator_id`, `editor_id`).
- Timestamps: `created_at` (`DateTime`, `default=func.now()`), `updated_at` (`DateTime`, `onupdate=func.now()`).
- Relationships via `relationship(..., back_populates=...)`.

### Views

- Class-based views inheriting nothing special — decorated with `@view_config(...)`.
- Views live in `marker/views/<entity>.py`.
- `request.dbsession` — the SQLAlchemy session.
- `request.identity` — the authenticated `User` object (or `None`).
- `request.translate` — i18n callable for user-facing strings.
- Redirects use `HTTPSeeOther`, not `HTTPFound`.
- Forbidden unauthenticated requests redirect with **303 See Other** to `/login?next=...`.
- HTMX partial updates return `htmx_refresh_response()` from `marker.views`.
- Sorting uses `sort_column()` and `apply_order()` from `marker.views`.
- Polish alphabetical sort uses `polish_sort_expression()`.
- Safe redirect validation uses `safe_redirect_target(request, url, fallback)`.

### Forms

- WTForms subclassing `Form` from `marker.forms`.
- `TranslationString` labels use `marker.forms.ts` — do not call `str()` on them in tests; patch `TranslationString.__str__` to return `.msg` instead.

### Alembic Migrations

- File naming: `YYYYMMDD_<revid>.py` (configured via `file_template` in `development.ini`).
- Current head revision: `9ca296fb5e5a` (consolidated migration, May 2026).
- Always run `alembic upgrade head` after creating a new revision.
- To squash: generate autogenertion against empty DB, replace revision ID, rename file, verify with `current`.

### Exports

- `make_export_response(request, rows, header_row, row_colors=None)` dispatches to `response_xlsx` or `response_ods` based on `request.params.get("format")`.
- XLSX content-type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`.
- ODS content-type: `application/vnd.oasis.opendocument.spreadsheet`.

---

## Testing Conventions

### Fixtures (from `tests/conftest.py`)

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `dbengine` | session | Creates engine, runs `alembic upgrade head` |
| `dbsession` | function | Transaction-scoped session, aborted after each test |
| `testapp` | function | WebTest `TestApp` against the full WSGI app |
| `app_request` | function | Real Pyramid request inside a prepare context |

### Rules

- Tests use `dbsession` for unit/integration tests against the real DB.
- `testapp` is used for full functional (HTTP-level) tests.
- All tests must be in English.
- **100% coverage is required** — add tests for every new branch.
- Do not write trivially-true assertions like `assert result is not None` after view calls that always return a response object. Assert on specific attributes:
  - View returning a dict → assert specific keys/values in the dict.
  - View returning an HTTP response (export) → assert `result.content_type` contains the expected MIME type.
  - View returning a redirect → assert `result.location` or use `testapp` and check the `Location` header.
- The `integration` marker is reserved for tests hitting external services (Nominatim, etc.) — they are not run by default.
- Do not create stub/mock functions in production code solely for test compatibility.

### Common Patterns

```python
# Unit test with dbsession
def test_something(dbsession):
    user = User(name="u1", fullname="U1", email="u@x.com", role="user", password="x")
    dbsession.add(user)
    dbsession.flush()
    assert user.id is not None

# Functional test
def test_redirect_to_login(testapp):
    res = testapp.get("/company/add", status=303)
    assert "/login" in res.headers["Location"]

# Export test
def test_export_returns_xlsx(dbsession):
    ...
    result = view.export_companies()
    assert "vnd.openxmlformats-officedocument" in result.content_type
```

---

## Workflow Checklist

After every change:

1. [ ] Code and comments written in English
2. [ ] `uv run isort .` and `uv run black .` run
3. [ ] New/changed user-facing strings extracted and translations updated (if applicable):
   - `uv run pybabel extract -F babel.cfg -o marker/locale/messages.pot .`
   - `uv run pybabel update -i marker/locale/messages.pot -d marker/locale`
   - Remove `fuzzy` flags from `.po` files
   - `uv run pybabel compile -d marker/locale`
4. [ ] Alembic migration created and applied if models changed:
   - `uv run alembic -c development.ini revision --autogenerate -m "..."`
   - `uv run alembic -c development.ini upgrade head`
5. [ ] Tests added/updated for all new or changed code
6. [ ] `uv run pytest --cov=marker --cov-report=term-missing` passes with **100% coverage**
7. [ ] Commit message prepared in English summarising the changes
