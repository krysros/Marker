<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div class="me-auto">${pills.pills(user_pills, active_url=request.route_url('user_projects', username=user.name))}</div>
  <div>${button.a(icon='download', color='primary', title='XLSX', url=request.route_url('user_export_projects', username=user.name, _query=q))}</div>
  <div>${button.a(icon='download', color='outline-primary', title='ODS', url=request.route_url('user_export_projects', username=user.name, _query={**q, 'format': 'ods'}))}</div>
  <div>${button.a(icon='map', color='secondary', url=request.route_url('user_map_projects', username=user.name))}</div>
</div>

<p class="lead">${user.fullname}</p>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <%include file="project_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="project_table.mako"/>