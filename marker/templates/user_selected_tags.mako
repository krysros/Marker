<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-tags"></i> ${_("Selected tags")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.button(icon='square', color='warning', url=request.route_url('user_clear_selected_tags', username=user.name))}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown(dd_sort)}</div>
  <div class="me-auto">${button.dropdown(dd_order)}</div>
  <div>${button.a_button(icon='download', color='primary', url=request.route_url('user_export_selected_tags', username=user.name, _query={'sort': dd_sort._sort, 'order': dd_order._order}))}</div>
</div>

<%include file="tag_table.mako"/>