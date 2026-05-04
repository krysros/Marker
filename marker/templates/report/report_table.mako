<%!
  from decimal import Decimal

  _DECIMAL_REPORTS = {
      "projects-highest-value",
      "projects-highest-usable-area",
      "projects-highest-cubic-volume",
  }

  def fmt_decimal(value):
      if value is None:
          return "---"
      parts = f"{value:,.2f}".split(".")
      parts[0] = parts[0].replace(",", "\u202f")
      return ".".join(parts)
%>

<%def name="rows()">
% for k, v in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
<%
  result_url = None
  if rel == "companies-tags":
      result_url = request.route_url("company_all", _query={"tag": k})
  elif rel == "projects-tags":
      result_url = request.route_url("project_all", _query={"tag": k})
  elif rel == "companies-subdivisions":
      result_url = request.route_url("company_all", _query={"subdivision": k})
  elif rel == "projects-subdivisions":
      result_url = request.route_url("project_all", _query={"subdivision": k})
  elif rel == "companies-cities":
      result_url = request.route_url("company_all", _query={"city": k})
  elif rel == "projects-cities":
      result_url = request.route_url("project_all", _query={"city": k})
  elif rel in {"users-companies", "users-projects"}:
      result_url = request.route_url("user_all", _query={"name": k})
  elif rel in {
      "companies-comments",
      "companies-projects",
      "companies-stars",
      "companies-announcement",
      "companies-tenders",
      "companies-constructions",
      "designers",
      "purchasers",
      "investors",
      "general-contractors",
      "subcontractors",
      "suppliers",
  }:
      result_url = request.route_url("company_all", _query={"name": k})
  elif rel in {
      "projects-comments",
      "projects-stars",
      "projects-companies",
      "projects-highest-value",
      "projects-highest-usable-area",
      "projects-highest-cubic-volume",
  }:
      result_url = request.route_url("project_all", _query={"name": k})
  if "subdivisions" in rel:
      label = get_subdivision_name(k, "---")
  else:
      label = k or "---"
%>
% if result_url:
  <td><a href="${result_url}">${label}</a></td>
% else:
  <td>${label}</td>
% endif
% if rel in _DECIMAL_REPORTS:
  <td>${fmt_decimal(v)}</td>
% else:
  <td>${v}</td>
% endif
</tr>
% endfor
</%def>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>${_("Description")}</th>
        <th>${_("Number")}</th>
      </tr>
    </thead>
    <tbody>
      ${rows()}
    </tbody>
  </table>
</div>