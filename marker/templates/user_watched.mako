<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-eye"></i> ${_("Watched")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.button(icon='eye', color='warning', url=request.route_url('user_clear_watched', username=user.name))}
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
      <div class="mb-3">
        ${form.status.label}
        ${form.status(class_="form-control")}
      </div>
      <button type="submit" class="btn btn-primary">${_("Submit")}</button>
    </form>
  </div>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div class="me-auto">${button.dropdown_order(order_criteria)}</div>
  <div>${button.a_button(icon='download', color='primary', url=request.route_url('user_export_watched', username=user.name, _query=q))}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="project_table.mako"/>