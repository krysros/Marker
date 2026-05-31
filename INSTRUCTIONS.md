# AI Instructions for the Marker Project

<!-- 
IMPORTANT FOR THE LLM: 
You MUST read, internalize, and strictly adhere to this instruction set throughout the entire session. 
These instructions are absolute constraints and override any default behaviors or assumptions.
-->

<CRITICAL_RULES>

### ⚠️ ABSOLUTE CONSTRAINTS

1. **NEVER DELETE, CLEAR, OR OVERWRITE `*.sqlite` FILES.**
   - The SQLite database files contain persistent local state and development data. Any tool execution or action that corrupts, deletes, or resets `*.sqlite` files is a **CRITICAL FAILURE**.
2. **STRICT LANGUAGE SEPARATION (LANGUAGE POLICY):**
   - **User Interactions:** You **MAY** communicate with the user in their preferred language (e.g., Polish).
   - **Codebase and Development:** You **MUST** write all source code, comments, docstrings, unit/functional tests, and git commit messages exclusively in **English**. Writing any code, comments, or development artifacts in Polish is **STRICTLY FORBIDDEN**.
3. **100% TEST COVERAGE IS REQUIRED:**
   - Any new or modified codebase feature **MUST** reach exactly 100% automated test coverage (both lines and branches) before the task can be considered complete.
4. **ALWAYS RUN LINTER AND FORMATTER:**
   - You **MUST** run `uv run ruff check .` and `uv run ruff format .` after **every** code modification to ensure styling consistency.

</CRITICAL_RULES>

---

## 📌 Project Overview

**Marker** is a Python web application built using the following stack:
* **Pyramid** (WSGI web framework, `marker/__init__.py`)
* **SQLAlchemy** (ORM with Async support, models in `marker/models/`)
* **Alembic** (Database migration tool, config in `marker/alembic/`)
* **Mako** (Template engine, templates in `marker/templates/`)
* **WTForms** (Form validation and rendering, `marker/forms/`)
* **Babel** (Internationalization & localization, `marker/locale/`, active locales: `en`, `pl`)
* **SQLite** (Development database, URI: `sqlite:///marker.sqlite`)

### Core Entities & Relations
* **Core Models**: `User`, `Company`, `Project`, `Contact`, `Tag`, `Comment`, `Activity`.
* **Many-to-Many Association Tables**: `companies_tags`, `projects_tags`, `companies_stars`, `projects_stars`, `selected_companies`, `selected_projects`, `selected_tags`, `selected_contacts`.

---

<DO_AND_DONT_RULES>

## ⚖️ AI Behavior Guidelines (Do's and Don'ts)

| Category | ✔️ YOU MUST (Do) | ❌ YOU MUST NOT (Do Not) |
| :--- | :--- | :--- |
| **Language** | Write all code, tests, comments, and commit messages in **English**. | **NEVER** write code comments, docstrings, or commits in Polish or other languages. |
| **Testing** | Write thorough unit/functional tests.<br>Assert on specific attributes, keys, or response headers. | Do **NOT** write trivially-true assertions (e.g., `assert result is not None` when a response is guaranteed). |
| **Database** | Create an `Activity(company=co, project=proj)` instance to link Companies & Projects. | Do **NOT** use direct append like `co.projects.append(proj)` (causes SQLAlchemy backref `KeyError`). |
| **Dependencies**| **ALWAYS** execute commands using the `uv` package manager within the venv context. | Do **NOT** use global `pip` or system python folders for installations. |
| **Form Labels** | Patch `TranslationString.__str__` to return `.msg` in tests. | Do **NOT** call `str()` on `TranslationString` labels in tests without patching. |
| **HTTP Views** | Return `HTTPSeeOther` (303 Redirect) for web redirects. | Do **NOT** use `HTTPFound` (302 Redirect). |

</DO_AND_DONT_RULES>

---

## 📂 Project Layout

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

<COMMANDS>

## 💻 Development & Workflow Commands

All Python commands **MUST** be run using `uv` inside the virtual environment.

```bash
# 1. Install dependencies
uv sync

# 2. Run local development server
uv run pserve development.ini

# 3. Run entire test suite
uv run pytest

# 4. Run tests with coverage (STRICT 100% COVERAGE VERIFICATION)
uv run pytest --cov=marker --cov-report=term-missing

# 5. Lint and format code (Run after EVERY code modification)
uv run ruff check .
uv run ruff format .

# 6. Database Migrations via Alembic
uv run alembic -c development.ini revision --autogenerate -m "description"
uv run alembic -c development.ini upgrade head
uv run alembic -c development.ini current
uv run alembic -c development.ini history

# 7. Localization & i18n via Babel (extract, update, compile)
uv run pybabel extract -F babel.cfg -o marker/locale/messages.pot .
uv run pybabel update -i marker/locale/messages.pot -d marker/locale
# Note: Manually remove `fuzzy` flags from .po files before compiling
uv run pybabel compile -d marker/locale
```

</COMMANDS>

---

<TECHNICAL_STANDARDS>

## 🛠️ Technical Standards

### 1. Models & Database
* **Base Class**: Inherit from `Base` (`marker.models.meta`).
* **Naming Conventions**: Use the SQLAlchemy naming convention defined in `meta.py` (`NAMING_CONVENTION`).
* **Foreign Keys Cascade**: Use `ondelete="CASCADE"` for ownership-level relations, and `ondelete="SET NULL"` for soft-references (e.g., `creator_id`, `editor_id`).
* **Timestamps**: `created_at` (`DateTime`, `default=lambda: datetime.datetime.now(UTC)`), `updated_at` (`DateTime`, `onupdate=func.now()`).
* **Count Helper**: Use `CountMixin` from `meta.py` which provides the `_scalar_count(stmt)` helper for model classes requiring scalar count queries.
* **ORM Relationships**: Declare relationships using explicit `relationship(..., back_populates=...)`.

### 2. HTTP Views
* **Structure**: Class-based views decorated with `@view_config(...)` located in `marker/views/<entity>.py`.
* **Database Session**: Access the active transaction-scoped session via `request.dbsession`.
* **User Identity**: Retrieve the authenticated `User` object (or `None`) via `request.identity`.
* **Internationalization**: Translate user-facing strings using `request.translate(_("..."))`.
* **Redirects**: Always use `HTTPSeeOther` (303 status code), never `HTTPFound` (302 status code).
* **Unauthorized Access**: Forbidden unauthenticated requests **MUST** redirect with a **303 See Other** status code to `/login?next=...`.
* **HTMX Support**: Return `htmx_refresh_response()` from `marker.views` for partial HTMX updates.
* **Sorting & Ordering**: Use `sort_column()` and `apply_order()` from `marker.views`. For Polish alphabetical sorting, use `polish_sort_expression()`.
* **Safe Redirect Validation**: **MUST** validate targets using `safe_redirect_target(request, url, fallback)`.

### 3. Forms
* **WTForms Subclassing**: Subclass `Form` from `marker.forms`.
* **Form Labels**: Labels **MUST** use translation strings defined in `marker.forms.ts`.

### 4. Alembic Migrations
* **Migration Template**: Naming format `YYYYMMDD_<revid>.py` (configured in `development.ini`).
* **Current DB Head**: `9ca296fb5e5a` (consolidated migration, May 2026).
* **Upgrade Requirement**: Always execute `alembic upgrade head` after generating a new migration revision.

### 5. Spreadsheet Exports
* **Dispatching**: `make_export_response(request, rows, header_row, row_colors=None)` automatically handles formatting (`response_xlsx` or `response_ods`) based on `request.params.get("format")`.
* **MIME Types**:
  * XLSX: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
  * ODS: `application/vnd.oasis.opendocument.spreadsheet`

</TECHNICAL_STANDARDS>

---

<TESTING_CONVENTIONS>

## 🧪 Testing Conventions

### Core Fixtures (`tests/conftest.py`)

| Fixture | Scope | Description |
| :--- | :--- | :--- |
| `dbengine` | session | Sets up the SQLite engine and runs `alembic upgrade head`. |
| `dbsession` | function | Transaction-scoped session, automatically aborted/rolled back after each test. |
| `testapp` | function | WebTest `TestApp` configuration against the full Pyramid WSGI application. |
| `app_request` | function | Real preconfigured Pyramid request instance inside a request-preparation context. |

### Strict Assertion Rules
When testing HTTP views, **DO NOT** use trivial or redundant assertions like `assert result is not None` when a view always returns a response object. You **MUST** assert on specific structural elements:
1. **Views returning a dictionary**: Assert on specific keys/values inside the returned dict.
2. **Views returning an HTTP Export response**: Assert on `result.content_type` matching the expected spreadsheet MIME type.
3. **Views returning Redirects**: Assert on `result.location` or verify headers in a functional test.
4. **Integration Marker**: The `@pytest.mark.integration` marker is strictly reserved for tests hitting real external services (e.g., Nominatim, LLM APIs). These are skipped during standard test runs.

### Example Test Patterns

```python
# 1. Unit Test utilizing transaction-scoped dbsession
def test_something(dbsession):
    user = User(name="u1", fullname="U1", email="u@x.com", role="user", password="x")
    dbsession.add(user)
    dbsession.flush()
    assert user.id is not None

# 2. Functional Test utilizing WebTest TestApp
def test_redirect_to_login(testapp):
    res = testapp.get("/company/add", status=303)
    assert "/login" in res.headers["Location"]

# 3. View Export Test
def test_export_returns_xlsx(dbsession):
    ...
    result = view.export_companies()
    assert "vnd.openxmlformats-officedocument" in result.content_type
```

</TESTING_CONVENTIONS>

---

<WORKFLOW_CHECKLIST>

## 🏁 Workflow Checklist

Before ending any task, you **MUST** ensure the following checklist is fully completed:

1. [ ] Run `uv run ruff check .` and `uv run ruff format .` and resolve all lint issues.
2. [ ] Extract and compile updated user-facing strings (if applicable):
   - `uv run pybabel extract -F babel.cfg -o marker/locale/messages.pot .`
   - `uv run pybabel update -i marker/locale/messages.pot -d marker/locale`
   - Compile translation catalogs using `uv run pybabel compile -d marker/locale` (after verifying po files).
3. [ ] If models were modified, generate and run migrations:
   - `uv run alembic -c development.ini revision --autogenerate -m "..."`
   - `uv run alembic -c development.ini upgrade head`
4. [ ] Run `uv run pytest --cov=marker --cov-report=term-missing` and verify **100% coverage** and **0 failing tests**.

</WORKFLOW_CHECKLIST>
