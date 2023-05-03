<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<%!
  import pycountry
%>

<h2>
  <i class="bi bi-briefcase"></i> ${_("Projects")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a_button(icon='map', color='secondary', url=request.route_url('project_map', _query=search_query))}
    ${button.a_button(icon='search', color='primary', url=request.route_url('project_search'))}
    ${button.a_button(icon='plus-lg', color='success', url=request.route_url('project_add'))}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <div class="dropdown">
    <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
      <i class="bi bi-filter"></i> ${_("Filter")}
    </button>
    <form class="dropdown-menu p-4">
      <div class="mb-3">
        ${filter_form.status.label}
        ${filter_form.status(class_="form-control")}
      </div>
      <div class="mb-3">
        ${filter_form.color.label}
        ${filter_form.color(class_="form-control")}
      </div>
      <div class="mb-3">
        ${filter_form.country.label}
        ${filter_form.country(class_="form-control", **{"hx-get": f"{request.route_url('subdivision')}", "hx-target": "#subdivision"})}
      </div>
      <div class="mb-3">
        ${filter_form.subdivision.label}
        ${filter_form.subdivision(class_="form-control")}
      </div>
      ${filter_form.submit(class_="btn btn-primary")}
    </form>
  </div>
  <div>${button.dropdown(dd_sort)}</div>
  <div>${button.dropdown(dd_order)}</div>
</div>

% if any(x for x in search_query.values() if x):
<div class="alert alert-info" role="alert">
  <strong>${_("Search criteria")}: </strong>
  % for k, v in search_query.items():
    ${k}:
    % if isinstance(v, list):
      <strong>${", ".join(v)}</strong>;
    % else:
      <strong>${v}</strong>;
    % endif
  % endfor
</div>
% endif

<%include file="project_table.mako"/>