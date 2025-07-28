<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-star"></i> ${_("Projects")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a(icon='map', color='secondary', url=request.route_url('user_map_projects_stars', username=user.name))}
    ${button.button(icon='star', color='warning', url=request.route_url('user_clear_projects_stars', username=user.name))}
    ${button.a(icon='download', color='primary', url=request.route_url('user_export_projects_stars', username=user.name, _query=q))}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <%include file="project_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div class="me-auto">${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="project_table.mako"/>