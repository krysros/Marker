<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>


<h2><i class="bi bi-briefcase"></i> Projekty
  <div class="float-end">
    ${button.map('project_map')}
    ${button.search('project_search')}
    ${button.add('project_add')}
  </div>
</h2>

<hr>

<div class="card border-0">
  <div class="row">
    <div class="col">
      ${dropdown.filter_button('project_all', dropdown_status)}
      ${dropdown.sort_button('project_all', dropdown_sort)}
      ${dropdown.order_button('project_all', dropdown_order)}
    </div>
  </div>
</div>

<%include file="project_table.mako"/>