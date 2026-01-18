<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-check-square"></i> ${_("Tags")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.delete_selected(url=request.route_url('user_delete_selected_tags', username=user.name))}
    ${button.button(icon='square', color='warning', url=request.route_url('user_clear_selected_tags', username=user.name))}
    ${button.a(icon='download', color='primary', url=request.route_url('user_export_selected_tags', username=user.name, _query=q))}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div class="me-auto">${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="tag_table.mako"/>