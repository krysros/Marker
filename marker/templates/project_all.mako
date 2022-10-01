<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card">
  <div class="card-body">
    ${dropdown.filter_button('project_all', dropdown_status)}
    ${dropdown.sort_button('project_all', dropdown_sort)}
    ${dropdown.order_button('project_all', dropdown_order)}
    <div class="float-end">
      ${button.search('project_search')}
      ${button.add('project_add')}
    </div>
  </div>
</div>

<%include file="project_table.mako"/>