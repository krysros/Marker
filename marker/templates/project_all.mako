<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card">
  <div class="card-body">
    ${dropdown.filter_button('project_all', dropdown_status, filter=filter, sort=sort, order=order)}
    ${dropdown.sort_button('project_all', dropdown_sort, filter=filter, sort=sort, order=order)}
    ${dropdown.order_button('project_all', dropdown_order, filter=filter, sort=sort, order=order)}
    <div class="float-end">
      ${button.search('project_search')}
      ${button.add('project_add')}
    </div>
  </div>
</div>

<%include file="project_table.mako"/>