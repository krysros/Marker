<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<form id="export-checked" action="${request.route_url('user_checked_export', username=user.name)}" method="post">
  <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
  <input type="hidden" name="sort" value=${sort}>
  <input type="hidden" name="order" value=${order}>
</form>

<div class="card">
  <div class="card-body">
    ${dropdown.sort_button('user_checked', dropdown_sort, filter=None, sort=sort, order=order, username=user.name)}
    ${dropdown.order_button('user_checked', dropdown_order, filter=None, sort=sort, order=order, username=user.name)}
    <div class="float-end">
      <button type="submit" class="btn btn-primary" form="export-checked" value="submit">Eksportuj</button>
      ${button.danger('user_checked_clear', 'Wyczyść', username=user.name)}
    </div>
  </div>
</div>

<%include file="company_table.mako"/>