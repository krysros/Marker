<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-check-square"></i> ${_("Projects")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.clear('user_clear_selected_projects', icon='square', username=user.name)}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('user_selected_projects', dd_filter, username=user.name)}</div>
  <div>${button.dropdown('user_selected_projects', dd_sort, username=user.name)}</div>
  <div class="me-auto">${button.dropdown('user_selected_projects', dd_order, username=user.name)}</div>
  <div>${button.export('user_export_selected_projects', username=user.name, _query={'filter': dd_filter._filter, 'sort': dd_sort._sort, 'order': dd_order._order})}</div>
</div>

<%include file="project_table.mako"/>