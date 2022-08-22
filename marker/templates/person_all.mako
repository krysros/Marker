<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>

<div class="card">
  <div class="card-body">
    ${dropdown.sort_button('person_all', dropdown_sort, sort=sort, order=order)}
    ${dropdown.order_button('person_all', dropdown_order, sort=sort, order=order)}
    <div class="float-end">
      <a class="btn btn-primary" href="${request.route_url('person_search')}" role="button">Szukaj</a>
    </div>
  </div>
</div>

<%include file="person_table.mako"/>