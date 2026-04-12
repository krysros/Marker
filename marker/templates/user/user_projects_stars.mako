<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-briefcase"></i> ${_("Projects marked with a star")}
    <span class="badge bg-secondary">${counter}</span>
  </h2>
  <div class="d-flex flex-wrap gap-2 justify-content-md-end w-100 w-md-auto">
    ${button.a(icon='map', color='secondary', url=request.route_url('user_map_projects_stars', username=user.name))}
    ${button.button(icon='star', color='warning', url=request.route_url('user_clear_projects_stars', username=user.name))}
    ${button.dropdown_download(url_xlsx=request.route_url('user_export_projects_stars', username=user.name, _query=q), url_ods=request.route_url('user_export_projects_stars', username=user.name, _query={**q, 'format': 'ods'}))}
  </div>
</div>
<hr>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <%include file="project_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div class="me-auto">${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="project_table.mako"/>