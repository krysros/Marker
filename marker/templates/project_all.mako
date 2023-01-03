<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-briefcase"></i> Projekty
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.map('project_map', _query=search_query)}
    ${button.search('project_search')}
    ${button.add('project_add')}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('project_all', dd_filter)}</div>
  <div>${button.dropdown('project_all', dd_sort)}</div>
  <div>${button.dropdown('project_all', dd_order)}</div>
</div>

<%include file="project_table.mako"/>