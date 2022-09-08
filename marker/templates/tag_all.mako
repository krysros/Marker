<%include file="navbar.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>

<div class="card">
  <div class="card-body">
    ${dropdown.sort_button('tag_all', dropdown_sort, filter=None, sort=sort, order=order)}
    ${dropdown.order_button('tag_all', dropdown_order, filter=None, sort=sort, order=order)}
    <div class="float-end">
      <a class="btn btn-primary" role="button" href="#top" hx-get="${request.route_url('tag_search')}" hx-target="#main-container">Szukaj</a>
      <a class="btn btn-success" role="button" href="#top" hx-get="${request.route_url('tag_add')}" hx-target="#main-container">Dodaj</a>
    </div>
  </div>
</div>

<%include file="tag_table.mako"/>