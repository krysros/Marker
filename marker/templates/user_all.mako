<%include file="navbar.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>

<div class="card">
  <div class="card-body">
    ${dropdown.filter_button('user_all', roles, filter=filter, sort=sort, order=order)}
    ${dropdown.sort_button('user_all', dropdown_sort, filter=filter, sort=sort, order=order)}
    ${dropdown.order_button('user_all', dropdown_order, filter=filter, sort=sort, order=order)}
    <div class="float-end">
      <a class="btn btn-primary" role="button" href="#" hx-get="${request.route_url('user_search')}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Szukaj</a>
      <a class="btn btn-success" role="button" href="#" hx-get="${request.route_url('user_add')}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Dodaj</a>
    </div>
  </div>
</div>

<%include file="user_table.mako"/>