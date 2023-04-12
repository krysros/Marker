<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-hand-thumbs-up"></i> ${_("Recommended")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.clear('user_clear_recommended', icon='hand-thumbs-up', username=user.name)}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('user_recommended', dd_filter, username=user.name)}</div>
  <div>${button.dropdown('user_recommended', dd_sort, username=user.name)}</div>
  <div class="me-auto">${button.dropdown('user_recommended', dd_order, username=user.name)}</div>
  <div>${button.button('user_export_recommended', color='primary', icon='download', username=user.name, _query={'filter': dd_filter._filter, 'sort': dd_sort._sort, 'order': dd_order._order})}</div>
</div>

<%include file="company_table.mako"/>
