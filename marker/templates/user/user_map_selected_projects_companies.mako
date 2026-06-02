<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-buildings"></i> ${_("Companies of selected projects")}
  <span class="badge bg-secondary">${counter}</span>
</h2>
<hr>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <%include file="company_filter.mako"/>
  <div class="vr mx-1"></div>
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
  <div class="vr mx-1"></div>
  <%
    matched_route_name = getattr(request, "matched_route", None).name if getattr(request, "matched_route", None) else ""
  %>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}">
    <a class="btn ${'btn-primary' if matched_route_name == 'user_selected_projects_companies' else 'btn-outline-primary'}" href="${request.route_url('user_selected_projects_companies', username=user.name, _query=q)}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn ${'btn-primary' if matched_route_name == 'user_map_selected_projects_companies' else 'btn-outline-primary'}" href="${request.route_url('user_map_selected_projects_companies', username=user.name, _query=q)}"><i class="bi bi-map"></i> ${_("Map")}</a>
  </div>
  <div class="vr mx-1"></div>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_projects_tags', username=user.name)}"><i class="bi bi-tags"></i> ${_("Tags")}</a>
    <a class="btn btn-primary" href="${request.route_url('user_selected_projects_companies', username=user.name, _query=q)}"><i class="bi bi-buildings"></i> ${_("Companies")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_projects', username=user.name)}"><i class="bi bi-briefcase"></i> ${_("Projects")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_projects_contacts', username=user.name)}"><i class="bi bi-people"></i> ${_("Contacts")}</a>
  </div>
</div>

<div id="map"></div>

<%include file="/common/markers.mako"/>
