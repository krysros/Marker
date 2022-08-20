<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="modal" file="modal.mako"/>

<form id="user-checked-export" action="${request.route_url('user_checked_export', username=user.name)}" method="post">
  <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
  <input type="hidden" name="sort" value=${sort}>
  <input type="hidden" name="order" value=${order}>
</form>

<div class="card">
  <div class="card-body">
    ${dropdown.sort_button('user_checked', dropdown_sort, filter=None, sort=sort, order=order, username=user.name)}
    ${dropdown.order_button('user_checked', dropdown_order, filter=None, sort=sort, order=order, username=user.name)}
    <div class="float-end">
      <button type="submit" class="btn btn-primary" form="user-checked-export" value="submit">Eksportuj</button>
      ${modal.danger_dialog('user_checked_clear', 'Wyczyść', 'Wyczyścić zaznaczone pozycje? Ta operacja nie usuwa firm z bazy danych.', username=user.name)}
    </div>
  </div>
</div>

<%include file="company_table.mako"/>