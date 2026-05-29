import re
import os


from ..forms.ts import TranslationString as _
from .langchain_ai import invoke_text

_SCHEMA_CONTEXT = """\
You are a SQL query generator for a CRM database.
Generate only a single valid SQL SELECT statement.
Output raw SQL only — no markdown, no code blocks, no explanations.

Database schema:
  companies      (id, name, street, postcode, city, subdivision, country, latitude, longitude,
                  website, color, NIP, REGON, KRS, created_at, updated_at, creator_id, editor_id)
  projects       (id, name, street, postcode, city, subdivision, country, latitude, longitude,
                  website, color, deadline, stage, object_category, delivery_method,
                  usable_area, cubic_volume, created_at, updated_at, creator_id, editor_id)
  contacts       (id, name, role, phone, email, color, created_at, updated_at,
                  creator_id, editor_id, company_id, project_id)
  tags           (id, name, created_at, updated_at, creator_id, editor_id)
  users          (id, name, fullname, email, role, created_at, updated_at)
  comments       (id, body, created_at, updated_at, creator_id, editor_id, company_id, project_id)
  activity       (company_id, project_id, stage, role, currency, value_net, value_gross)
  companies_tags (company_id, tag_id)
  projects_tags  (project_id, tag_id)

Relationships:
- companies ↔ projects is many-to-many via the activity table:
    JOIN activity ON companies.id = activity.company_id
    JOIN projects ON activity.project_id = projects.id
  There is NO company_id column in the projects table.
- companies ↔ tags via companies_tags
- projects  ↔ tags via projects_tags
- contacts belong to a company (contacts.company_id) or a project (contacts.project_id)
- comments  belong to a company (comments.company_id)  or a project (comments.project_id)

Rules:
- Output ONLY a SELECT statement (no INSERT, UPDATE, DELETE, DROP, etc.)
- Do not include semicolons inside the query
- Always add LIMIT 1000 (or fewer) at the end
- Use standard SQL compatible with SQLite
"""

_FORBIDDEN_KEYWORDS = (
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "TRUNCATE",
    "ALTER",
    "CREATE",
    "ATTACH",
    "PRAGMA",
    "VACUUM",
)


def get_configured_model() -> str:
    """
    Get the configured Gemini model name.
    Resolves in priority order:
    1. Active Pyramid request settings (gemini.model)
    2. Project configuration files (.ini)
    """
    # Try active Pyramid request settings
    try:
        from pyramid.threadlocal import get_current_request

        req = get_current_request()
        if (
            req is not None
            and hasattr(req, "registry")
            and hasattr(req.registry, "settings")
        ):
            conf_model = req.registry.settings.get("gemini.model")
            if conf_model:
                return conf_model
    except Exception:
        pass

    # Try reading from config files in the project root/parent directory
    for ini_name in ("development.ini", "testing.ini", "production.ini"):
        path = ini_name
        for depth in range(3):
            if os.path.exists(path):
                try:
                    from pyramid.paster import get_appsettings

                    settings = get_appsettings(path)
                    conf_model = settings.get("gemini.model")
                    if conf_model:
                        return conf_model
                except Exception:
                    pass
            path = os.path.join("..", path)

    raise ValueError(
        "Gemini model is not configured. Please set 'gemini.model' in your .ini file."
    )


def _get_locale(locale: str | None = None) -> str:
    if locale:
        return locale
    try:
        from pyramid.threadlocal import get_current_request

        req = get_current_request()
        if req is not None:
            loc = getattr(req, "locale_name", None)
            if loc:
                return loc
    except Exception:
        pass

    try:
        req = get_current_request()
        if (
            req is not None
            and hasattr(req, "registry")
            and hasattr(req.registry, "settings")
        ):
            loc = req.registry.settings.get("pyramid.default_locale_name")
            if loc:
                return loc
    except Exception:
        pass

    for ini_name in ("development.ini", "testing.ini", "production.ini"):
        path = ini_name
        for depth in range(3):
            if os.path.exists(path):
                try:
                    from pyramid.paster import get_appsettings

                    settings = get_appsettings(path)
                    loc = settings.get("pyramid.default_locale_name")
                    if loc:
                        return loc
                except Exception:
                    pass
            path = os.path.join("..", path)

    return "en"


def generate_report_sql(
    prompt: str,
    fallback_model: str | None = None,
    retries: int | None = None,
    locale: str | None = None,
) -> str:
    model = get_configured_model()
    fallback_model = fallback_model or os.environ.get("GEMINI_FALLBACK_MODEL")
    retries_value = retries
    if retries_value is None:
        retries_raw = os.environ.get("GEMINI_RETRIES")
        if retries_raw not in (None, ""):
            try:
                retries_value = max(0, int(retries_raw))
            except ValueError:
                retries_value = None

    loc = _get_locale(locale)
    lang_info = ""
    if loc.startswith("pl"):
        lang_info = (
            "\nUser request language is Polish. Note that:\n"
            "- 'firmy' maps to 'companies'\n"
            "- 'projekty' maps to 'projects'\n"
            "- 'kontakty' maps to 'contacts'\n"
            "- 'tagi' maps to 'tags'\n"
            "- 'użytkownicy' maps to 'users'\n"
            "- 'komentarze' maps to 'comments'\n"
            "- 'województwo' maps to 'subdivision'\n"
            "- 'miasto' maps to 'city'\n"
            "- 'NIP' / 'REGON' / 'KRS' are company identifier columns\n"
            "Translate these concepts and filter values correctly to SQL."
        )
    else:
        lang_info = (
            "\nUser request language is English (or non-Polish). Generate the query accordingly."
        )

    full_context = f"{_SCHEMA_CONTEXT}{lang_info}\nUser request: {prompt}"

    sql = invoke_text(
        full_context,
        model=model,
        fallback_model=fallback_model,
        retries=2 if retries_value is None else retries_value,
        source="report_sql",
    )
    # Strip markdown code fences if Gemini wraps them anyway
    sql = re.sub(r"^```(?:sql)?\s*\n?", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\n?```\s*$", "", sql)
    return sql.strip()


def validate_sql(sql: str) -> str:
    stripped = sql.strip().lstrip(";").strip()
    if not stripped.upper().startswith("SELECT"):
        raise ValueError(str(_("Only SELECT statements are allowed.")))
    body = stripped.rstrip(";")
    if ";" in body:
        raise ValueError(str(_("Multiple SQL statements are not allowed.")))
    for kw in _FORBIDDEN_KEYWORDS:
        if re.search(r"\b" + kw + r"\b", body, re.IGNORECASE):
            raise ValueError(
                str(_("Keyword '%(kw)s' is not permitted in AI reports.")) % {"kw": kw}
            )
    return body
