<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-briefcase"></i> ${_("Selected projects")}
    <span class="badge bg-secondary">${counter}</span>
  </h2>
  <div class="d-flex flex-wrap gap-2 justify-content-md-end w-100 w-md-auto">
    ${button.delete_selected(url=request.route_url('user_delete_selected_projects', username=user.name, _query=q), confirm_text=_("Delete all selected projects?"))}
    <% from marker.utils.export_columns import project_cols; _export_cols = project_cols(_) %>
    ${button.dropdown_download_cols(request.route_url('user_export_selected_projects', username=user.name, _query=q), _export_cols)}
  </div>
</div>
<hr>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <%include file="project_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
  <a class="btn btn-sm btn-outline-secondary" href="${request.route_url('user_selected_projects_similar', username=user.name)}"><i class="bi bi-intersect"></i> ${_("Similar")}</a>
  <div class="btn-group btn-group-sm ms-auto" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-primary" href="${request.route_url('user_selected_projects', username=user.name, _query=q)}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_map_selected_projects', username=user.name, _query=q)}"><i class="bi bi-map"></i> ${_("Map")}</a>
  </div>
</div>

<%include file="project_table.mako"/>