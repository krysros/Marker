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
      % if form.name.data:
        ${form.name(class_="form-control")}
      % endif
      % if form.street.data:
        ${form.street(class_="form-control")}
      % endif
      % if form.postcode.data:
        ${form.postcode(class_="form-control")}
      % endif
      % if form.city.data:
        ${form.city(class_="form-control")}
      % endif
      <div class="mb-3">
        ${form.country.label}
        ${form.country(class_="form-control", **{"hx-get": f"{request.route_url('subdivision')}", "hx-target": "#subdivision"})}
      </div>
      <div class="mb-3">
        ${form.subdivision.label}
        ${form.subdivision(class_="form-control")}
        <small class="text-body-secondary">Ctrl + Click</small>
      </div>
      % if form.link.data:
        ${form.link(class_="form-control")}
      % endif
      % if form.NIP.data:
        ${form.NIP(class_="form-control")}
      % endif
      % if form.REGON.data:
        ${form.REGON(class_="form-control")}
      % endif
      % if form.KRS.data:
        ${form.KRS(class_="form-control")}
      % endif
      % if form.court.data:
        ${form.court(class_="form-control")}
      % endif
      <div class="mb-3">
        ${form.color.label}
        ${form.color(class_="form-control")}
      </div>
      <button type="submit" class="btn btn-primary">${_("Submit")}</button>
    </form>
  </div>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="company_table.mako"/>