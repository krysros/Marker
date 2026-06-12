<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-briefcase"></i> ${_("Projects marked with a star")}
  </h2>
  <div class="d-flex flex-wrap gap-2 justify-content-md-end w-100 w-md-auto">
    ${button.button(icon='star', color='warning', url=request.route_url('user_clear_projects_stars', username=user.name))}
  </div>
</div>
<hr>

<div id="main-container" hx-boost="true" hx-target="#main-container" hx-select="#main-container" hx-swap="outerHTML" hx-push-url="true">
<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <%include file="project_filter.mako"/>
  <div class="vr mx-1"></div>
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
  <div class="vr mx-1"></div>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}" hx-boost="false">
    <a class="btn btn-outline-primary" href="${request.route_url('user_projects_stars', username=user.name, _query=q)}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_map_projects_stars', username=user.name, _query=q)}"><i class="bi bi-map"></i> ${_("Map")}</a>
  </div>
  <div class="vr mx-1"></div>
  ${button.dropdown_quality(
    uptime_url=request.route_url('user_uptime_projects_stars', username=user.name, _query=q),
    duplicates_url=request.route_url('user_projects_stars', username=user.name, _query={**q, 'duplicates': '1', 'no_location': None}),
    nolocation_url=request.route_url('user_projects_stars', username=user.name, _query={**q, 'duplicates': None, 'no_location': '1'}),
    is_uptime=matched_route_name == 'user_uptime_projects_stars',
    is_duplicates=q.get('duplicates') == '1',
    is_nolocation=q.get('no_location') == '1'
  )}
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
    <%include file="user_uptime_projects_stars_rows.mako"/>
  </tbody>
</table>
</div>
</div>
