<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-hand-thumbs-up"></i> ${_("Recommended")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.button(icon='hand-thumbs-up', color='warning', url=request.route_url('user_clear_recommended', username=user.name))}
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
        ${form.country.label}
        ${form.country(class_="form-control", **{"hx-get": f"{request.route_url('subdivision')}", "hx-target": "#subdivision"})}
      </div>
      <div class="mb-3">
        ${form.subdivision.label}
        ${form.subdivision(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.color.label}
        ${form.color(class_="form-control")}
      </div>
      ${form.submit(class_="btn btn-primary")}
    </form>
  </div>
  <div>${button.dropdown(dd_sort)}</div>
  <div class="me-auto">${button.dropdown(dd_order)}</div>
  <div>${button.a_button(icon='download', color='primary', url=request.route_url('user_export_recommended', username=user.name, _query={**q, 'sort': dd_sort._sort, 'order': dd_order._order}))}</div>
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
