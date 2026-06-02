<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-buildings"></i> ${_("Companies of selected contacts")}
    <span class="badge bg-secondary">${counter}</span>
  </h2>
</div>
<hr>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts_companies', username=user.name, _query=q)}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-primary" href="${request.route_url('user_map_selected_contacts_companies', username=user.name, _query=q)}"><i class="bi bi-map"></i> ${_("Map")}</a>
  </div>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('Pivot view')}">
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts_tags', username=user.name)}"><i class="bi bi-tags"></i> ${_("Tags")}</a>
    <a class="btn btn-primary" href="${request.route_url('user_selected_contacts_companies', username=user.name, _query=q)}"><i class="bi bi-buildings"></i> ${_("Companies")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts_projects', username=user.name, _query=q)}"><i class="bi bi-briefcase"></i> ${_("Projects")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts', username=user.name, _query=q)}"><i class="bi bi-people"></i> ${_("Contacts")}</a>
  </div>
</div>

<div id="map"></div>

<%include file="markers.mako"/>
