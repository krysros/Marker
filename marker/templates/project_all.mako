<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<%!
  import pycountry
%>

<h2>
  <i class="bi bi-briefcase"></i> ${_("Projects")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a_button(icon='map', color='secondary', url=request.route_url('project_map', _query=q))}
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
        <small class="text-body-secondary">Ctrl + Click</small>
      </div>
      ${form.link(class_="form-control")}
      ${form.deadline(class_="form-control")}
      ${form.stage(class_="form-control")}
      ${form.delivery_method(class_="form-control")}
      <div class="mb-3">
        ${form.color.label}
        ${form.color(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.status.label}
        ${form.status(class_="form-control")}
      </div>
      <input class="btn btn-primary" id="submit" name="submit" type="submit" value="${_('Submit')}">
    </form>
  </div>
  <div>${button.dropdown(dd_sort)}</div>
  <div>${button.dropdown(dd_order)}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="project_table.mako"/>