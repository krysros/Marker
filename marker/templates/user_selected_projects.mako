<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-check-square"></i> ${_("Projects")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.button(icon='square', url=request.route_url('user_clear_selected_projects', username=user.name))}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown(dd_filter, url=request.route_url('user_selected_projects', username=user.name))}</div>
  <div>${button.dropdown(dd_sort, url=request.route_url('user_selected_projects', username=user.name))}</div>
  <div class="me-auto">${button.dropdown(dd_order, url=request.route_url('user_selected_projects', username=user.name))}</div>
  <div>${button.a_btn(icon='download', color='primary', url=request.route_url('user_export_selected_projects', username=user.name, _query={'filter': dd_filter._filter, 'sort': dd_sort._sort, 'order': dd_order._order}))}</div>
</div>

<%include file="project_table.mako"/>