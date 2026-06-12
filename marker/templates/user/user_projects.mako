<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>
<%! from marker.utils.export_columns import project_cols %>
<% _export_cols = project_cols(_) %>
<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <div class="me-auto">${pills.pills(user_pills, active_url=request.route_url('user_projects', username=user.name))}</div>
  <div>${button.dropdown_download_cols(request.route_url('user_export_projects', username=user.name, _query=q), _export_cols)}</div>
</div>

<p class="lead">${user.fullname}</p>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <%include file="project_filter.mako"/>
  <div class="vr mx-1"></div>
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
  <div class="vr mx-1"></div>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}">
    <a class="btn ${'btn-primary' if not context.get('q') or (q.get('duplicates') != '1' and q.get('no_location') != '1') else 'btn-outline-primary'}" href="${request.route_url('user_projects', username=user.name,_query={**q, 'duplicates': None, 'no_location': None} if context.get('q') else {})}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_map_projects', username=user.name, _query=q)}"><i class="bi bi-map"></i> ${_("Map")}</a>
  </div>
  <div class="vr mx-1"></div>
  ${button.dropdown_quality(
    uptime_url=request.route_url('user_uptime_projects', username=user.name),
    duplicates_url=request.route_url('user_projects', username=user.name, _query={**q, 'duplicates': '1', 'no_location': None}),
    nolocation_url=request.route_url('user_projects', username=user.name, _query={**q, 'duplicates': None, 'no_location': '1'}),
    is_uptime=matched_route_name == 'user_uptime_projects',
    is_duplicates=context.get('q') and q.get('duplicates') == '1',
    is_nolocation=context.get('q') and q.get('no_location') == '1'
  )}
</div>

<%include file="search_criteria.mako"/>

<%include file="project_table.mako"/>