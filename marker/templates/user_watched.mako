<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="modal" file="modal.mako"/>

<form id="export-watched" action="${request.route_url('user_watched_export', username=user.name)}" method="post">
  <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
  <input type="hidden" name="filter" value=${filter}>
  <input type="hidden" name="sort" value=${sort}>
  <input type="hidden" name="order" value=${order}>
</form>

<div class="card">
  <div class="card-body">
    ${dropdown.filter_button('user_watched', progress, filter=filter, sort=sort, order=order, username=user.name)}
    ${dropdown.sort_button('user_watched', dropdown_sort, filter=filter, sort=sort, order=order, username=user.name)}
    ${dropdown.order_button('user_watched', dropdown_order, filter=filter, sort=sort, order=order, username=user.name)}
    <div class="float-end">
      <button type="submit" class="btn btn-primary" form="export-watched" value="submit">Eksportuj</button>
      ${modal.danger_dialog('user_watched_clear', 'Wyczyść', 'Wyczyścić wszystkie obserwowane projekty? Ta operacja nie usuwa projektów z bazy danych.', username=user.name)}
    </div>
  </div>
</div>

<%include file="project_table.mako"/>