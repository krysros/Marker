import re

from langchain_google_genai import ChatGoogleGenerativeAI

from ..forms.ts import TranslationString as _

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


def generate_report_sql(prompt: str, model: str = "gemini-2.5-flash-lite") -> str:
    llm = ChatGoogleGenerativeAI(model=model)
    response = llm.invoke(f"{_SCHEMA_CONTEXT}\nUser request: {prompt}")
    sql = response.content.strip()
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
