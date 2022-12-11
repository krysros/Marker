<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-briefcase"></i> Projekty
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.map('project_map')}
    ${button.search('project_search')}
    ${button.add('project_add')}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <div>${dropdown.filter_button('project_all', status)}</div>
  <div>${dropdown.sort_button('project_all', dropdown_sort)}</div>
  <div>${dropdown.order_button('project_all', dropdown_order)}</div>
</div>

<%include file="project_table.mako"/>