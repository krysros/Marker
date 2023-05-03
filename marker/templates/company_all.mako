<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<%!
  import pycountry
%>

<h2>
  <i class="bi bi-buildings"></i> ${_("Companies")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a_button(icon='map', color='secondary', url=request.route_url('company_map', _query=q))}
    ${button.a_button(icon='search', color='primary', url=request.route_url('company_search'))}
    ${button.a_button(icon='plus-lg', color='success', url=request.route_url('company_add'))}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <div class="dropdown">
    <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
      <i class="bi bi-filter"></i> ${_("Filter")}
    </button>
    <form class="dropdown-menu p-4">
      ${form.name(class_="form-control")}
      ${form.street(class_="form-control")}
      ${form.postcode(class_="form-control")}
      ${form.city(class_="form-control")}
      <div class="mb-3">
        ${form.country.label}
        ${form.country(class_="form-control", **{"hx-get": f"{request.route_url('subdivision')}", "hx-target": "#subdivision"})}
      </div>
      <div class="mb-3">
        ${form.subdivision.label}
        ${form.subdivision(class_="form-control")}
      </div>
      ${form.link(class_="form-control")}
      ${form.NIP(class_="form-control")}
      ${form.REGON(class_="form-control")}
      ${form.KRS(class_="form-control")}
      ${form.court(class_="form-control")}
      <div class="mb-3">
        ${form.color.label}
        ${form.color(class_="form-control")}
      </div>
      ${form.submit(class_="btn btn-primary")}
    </form>
  </div>
  <div>${button.dropdown(dd_sort)}</div>
  <div>${button.dropdown(dd_order)}</div>
</div>

% if any(x for x in q.values() if x):
<div class="alert alert-info" role="alert">
  <strong>${_("Search criteria")}: </strong>
  % for k, v in q.items():
    ${k}:
    % if isinstance(v, list):
      <strong>${", ".join(v)}</strong>;
    % else:
      <strong>${v}</strong>;
    % endif
  % endfor
</div>
% endif

<%include file="company_table.mako"/>