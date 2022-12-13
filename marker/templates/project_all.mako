<%inherit file="layout.mako"/>
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
  <div>${button.dropdown('project_all', items=status, criterion=filter, typ='filter', title='Status')}</div>
  <div>${button.dropdown('project_all', items=dropdown_sort, criterion=sort, typ='sort', title='Sortuj')}</div>
  <div>${button.dropdown('project_all', items=dropdown_order, criterion=order, typ='order', title='Kolejność')}</div>
</div>

<%include file="project_table.mako"/>