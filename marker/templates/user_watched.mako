<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<form id="export-watched" action="${request.route_url('user_watched_export', username=user.name)}" method="post">
  <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
  <input type="hidden" name="filter" value=${filter}>
  <input type="hidden" name="sort" value=${sort}>
  <input type="hidden" name="order" value=${order}>
</form>

<div class="card">
  <div class="card-body">
    ${dropdown.filter_button('user_watched', status, filter=filter, sort=sort, order=order, username=user.name)}
    ${dropdown.sort_button('user_watched', dropdown_sort, filter=filter, sort=sort, order=order, username=user.name)}
    ${dropdown.order_button('user_watched', dropdown_order, filter=filter, sort=sort, order=order, username=user.name)}
    <div class="float-end">
      <button type="submit" class="btn btn-primary" form="export-watched" value="submit">Eksportuj</button>
      ${button.danger('user_watched_clear', 'Wyczyść', username=user.name)}
    </div>
  </div>
</div>

<%include file="project_table.mako"/>