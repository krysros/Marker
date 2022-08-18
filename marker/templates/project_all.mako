<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>

<div class="card">
  <div class="card-body">
    ${dropdown.filter_button('project_all', dropdown_progress, filter=filter, sort=sort, order=order)}
    ${dropdown.sort_button('project_all', dropdown_sort, filter=filter, sort=sort, order=order)}
    ${dropdown.order_button('project_all', dropdown_order, filter=filter, sort=sort, order=order)}
    <div class="float-end">
      <a class="btn btn-primary" href="${request.route_url('project_search')}" role="button">Szukaj</a>
      <a class="btn btn-success" href="${request.route_url('project_add')}" role="button">Dodaj</a>
    </div>
  </div>
</div>

<%include file="project_table.mako"/>