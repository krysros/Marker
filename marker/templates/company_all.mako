<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>

<div class="card">
  <div class="card-body">
    ${dropdown.filter_button('company_all', colors, filter=filter, sort=sort, order=order)}
    ${dropdown.sort_button('company_all', dropdown_sort, filter=filter, sort=sort, order=order)}
    ${dropdown.order_button('company_all', dropdown_order, filter=filter, sort=sort, order=order)}
    <div class="float-end">
      <a class="btn btn-primary" href="${request.route_url('company_search')}" role="button">Szukaj</a>
      <a class="btn btn-success" href="${request.route_url('company_add')}" role="button">Dodaj</a>
    </div>
  </div>
</div>

<%include file="company_table.mako"/>