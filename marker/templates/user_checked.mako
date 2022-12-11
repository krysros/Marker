<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-check-square"></i> Zaznaczone
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.clear('user_checked_clear', icon='square', username=user.name)}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <div>${dropdown.filter_button('user_checked', colors, username=user.name)}</div>
  <div>${dropdown.sort_button('user_checked', dropdown_sort, username=user.name)}</div>
  <div class="me-auto">${dropdown.order_button('user_checked', dropdown_order, username=user.name)}</div>
  <div>${button.export('user_checked_export', username=user.name, _query={'filter': filter, 'sort': sort, 'order': order})}</div>
</div>

<%include file="company_table.mako"/>