<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>

<div class="card">
  <div class="card-body">
    ${dropdown.sort_button('tag_all', dropdown_sort, filter=None, sort=sort, order=order)}
    ${dropdown.order_button('tag_all', dropdown_order, filter=None, sort=sort, order=order)}
    <div class="float-end">
      <a class="btn btn-primary" href="${request.route_url('tag_search')}" role="button">Szukaj</a>
      <a class="btn btn-success" href="${request.route_url('tag_add')}" role="button">Dodaj</a>
    </div>
  </div>
</div>

<%include file="tag_table.mako"/>