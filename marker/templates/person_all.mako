<%include file="navbar.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>

<div class="card">
  <div class="card-body">
    ${dropdown.sort_button('person_all', dropdown_sort, sort=sort, order=order)}
    ${dropdown.order_button('person_all', dropdown_order, sort=sort, order=order)}
    <div class="float-end">
      <a class="btn btn-primary" role="button" href="#" hx-get="${request.route_url('person_search')}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Szukaj</a>
    </div>
  </div>
</div>

<%include file="person_table.mako"/>