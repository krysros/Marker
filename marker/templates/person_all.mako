<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-people"></i> Osoby
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.search('person_search')}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('person_all', dd_sort)}</div>
  <div>${button.dropdown('person_all', dd_order)}</div>
</div>

<%include file="person_table.mako"/>