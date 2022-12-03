<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-hand-thumbs-up"></i> Rekomendowane
  <div class="float-end">
    ${button.clear('user_recommended_clear', icon='hand-thumbs-up', username=user.name)}
  </div>
</h2>
<hr>

<div class="hstack gap-2">
  <div>${dropdown.sort_button('user_recommended', dropdown_sort, username=user.name)}</div>
  <div class="me-auto">${dropdown.order_button('user_recommended', dropdown_order, username=user.name)}</div>
  <div>${button.export('user_recommended_export', username=user.name, _query={'filter': filter, 'sort': sort, 'order': order})}</div>
</div>

<%include file="company_table.mako"/>
