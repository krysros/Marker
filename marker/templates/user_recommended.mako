<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-hand-thumbs-up"></i> Rekomendowane
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.clear('user_recommended_clear', icon='hand-thumbs-up', username=user.name)}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('user_recommended', dd_filter, username=user.name)}</div>
  <div>${button.dropdown('user_recommended', dd_sort, username=user.name)}</div>
  <div class="me-auto">${button.dropdown('user_recommended', dd_order, username=user.name)}</div>
  <div>${button.export('user_recommended_export', username=user.name, _query={'filter': dd_filter._filter, 'sort': dd_sort._sort, 'order': dd_order._order})}</div>
</div>

<%include file="company_table.mako"/>
