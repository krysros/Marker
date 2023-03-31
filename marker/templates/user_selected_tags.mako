<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-check-square"></i> ${_("Tags")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.clear('user_clear_selected_tags', icon='square', username=user.name)}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('user_selected_tags', dd_sort, username=user.name)}</div>
  <div class="me-auto">${button.dropdown('user_selected_tags', dd_order, username=user.name)}</div>
  <div>${button.export('user_export_selected_tags', username=user.name, _query={'sort': dd_sort._sort, 'order': dd_order._order})}</div>
</div>

<%include file="tag_table.mako"/>