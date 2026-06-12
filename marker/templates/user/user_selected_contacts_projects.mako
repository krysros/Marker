<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-briefcase"></i> ${_("Projects of selected contacts")}
    <span class="badge bg-secondary">${counter}</span>
  </h2>
  <div class="d-flex flex-wrap gap-2 justify-content-md-end w-100 w-md-auto">
    <% from marker.utils.export_columns import project_cols; _export_cols = project_cols(_) %>
    ${button.dropdown_download_cols(request.route_url('user_export_selected_contacts', username=user.name), _export_cols, extra_params={**q, 'category': 'projects'})}
  </div>
</div>
<hr>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <%include file="project_filter.mako"/>
  <div class="vr mx-1"></div>
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
  <div class="vr mx-1"></div>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}">
    <a class="btn ${'btn-primary' if not context.get('q') or (q.get('duplicates') != '1' and q.get('no_location') != '1') else 'btn-outline-primary'}" href="${request.route_url('user_selected_contacts_projects', username=user.name,_query={**q, 'duplicates': None, 'no_location': None} if context.get('q') else {})}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_map_selected_contacts_projects', username=user.name, _query=q)}"><i class="bi bi-map"></i> ${_("Map")}</a>
  </div>
  <div class="vr mx-1"></div>
  ${button.dropdown_quality(
    uptime_url=request.route_url('user_uptime_selected_contacts_projects', username=user.name),
    duplicates_url=request.route_url('user_selected_contacts_projects', username=user.name, _query={**q, 'duplicates': '1', 'no_location': None}),
    nolocation_url=request.route_url('user_selected_contacts_projects', username=user.name, _query={**q, 'duplicates': None, 'no_location': '1'}),
    is_uptime=matched_route_name == 'user_uptime_selected_contacts_projects',
    is_duplicates=context.get('q') and q.get('duplicates') == '1',
    is_nolocation=context.get('q') and q.get('no_location') == '1'
  )}
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('Pivot view')}">
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts_tags', username=user.name)}"><i class="bi bi-tags"></i> ${_("Tags")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts_companies', username=user.name, _query=q)}"><i class="bi bi-buildings"></i> ${_("Companies")}</a>
    <a class="btn btn-primary" href="${request.route_url('user_selected_contacts_projects', username=user.name, _query=q)}"><i class="bi bi-briefcase"></i> ${_("Projects")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts', username=user.name, _query=q)}"><i class="bi bi-people"></i> ${_("Contacts")}</a>
  </div>
</div>

<%include file="project_table.mako"/>
