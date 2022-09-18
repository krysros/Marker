<%include file="navbar.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<form id="export-recomended" action="${request.route_url('user_recomended_export', username=user.name)}" method="post">
  <input type="hidden" name="sort" value=${sort}>
  <input type="hidden" name="order" value=${order}>
</form>

<div class="card">
  <div class="card-body">
    ${dropdown.sort_button('user_recomended', dropdown_sort, filter=None, sort=sort, order=order, username=user.name)}
    ${dropdown.order_button('user_recomended', dropdown_order, filter=None, sort=sort, order=order, username=user.name)}
    <div class="float-end">
      <button type="submit" class="btn btn-primary" form="export-recomended" value="submit">Eksportuj</button>
      ${button.danger('user_recomended_clear', 'Wyczyść', 'Wyczyścić wszystkie rekomendacje? Ta operacja nie usuwa firm z bazy danych.', username=user.name)}
    </div>
  </div>
</div>

<%include file="company_table.mako"/>
