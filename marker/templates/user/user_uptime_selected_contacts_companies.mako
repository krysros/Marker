<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-buildings"></i> ${_("Companies of selected contacts")}
  </h2>
</div>
<hr>

<div id="main-container" hx-boost="true" hx-target="#main-container" hx-select="#main-container" hx-swap="outerHTML" hx-push-url="true">
<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <%include file="company_filter.mako"/>
  <div class="vr mx-1"></div>
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
  <div class="vr mx-1"></div>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}" hx-boost="false">
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts_companies', username=user.name, _query=q)}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_map_selected_contacts_companies', username=user.name, _query=q)}"><i class="bi bi-map"></i> ${_("Map")}</a>
  </div>
  <div class="vr mx-1"></div>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}" hx-boost="false">
    <a class="btn btn-primary" href="${request.route_url('user_uptime_selected_contacts_companies', username=user.name, _query=q)}"><i class="bi bi-globe"></i> ${_("Uptime")}</a>
    <a class="btn ${'btn-primary' if q.get('duplicates') == '1' else 'btn-outline-primary'}" href="${request.route_url('user_selected_contacts_companies', username=user.name, _query={**q, 'duplicates': '1', 'no_location': None})}"><i class="bi bi-files"></i> ${_("Duplicates")}</a>
    <a class="btn ${'btn-primary' if q.get('no_location') == '1' else 'btn-outline-primary'}" href="${request.route_url('user_selected_contacts_companies', username=user.name, _query={**q, 'duplicates': None, 'no_location': '1'})}"><i class="bi bi-geo"></i> ${_("No location")}</a>
  </div>
  <div class="btn-group btn-group-sm ms-auto" role="group" aria-label="${_('Pivot view')}">
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts_tags', username=user.name)}"><i class="bi bi-tags"></i> ${_("Tags")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts_companies', username=user.name)}"><i class="bi bi-buildings"></i> ${_("Companies")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts_projects', username=user.name)}"><i class="bi bi-briefcase"></i> ${_("Projects")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts', username=user.name)}"><i class="bi bi-people"></i> ${_("Contacts")}</a>
  </div>
</div>

<%include file="search_criteria.mako"/>

<div class="table-responsive">
<table class="table table-striped">
  <thead>
    <tr>
      <th>#</th>
      <th>${_("Name")}</th>
      <th>${_("Website")}</th>
      <th>${_("HTTP response code")}</th>
    </tr>
  </thead>
  <tbody id="uptime-tbody">
    <%include file="user_uptime_selected_contacts_companies_rows.mako"/>
  </tbody>
</table>
</div>
</div>
