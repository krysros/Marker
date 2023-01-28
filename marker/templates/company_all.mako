<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-buildings"></i> Firmy
  <small class="text-muted">${heading}</small>
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.map('company_map', _query=search_query)}
    ${button.search('company_search')}
    ${button.add('company_add')}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('company_all', dd_sort)}</div>
  <div>${button.dropdown('company_all', dd_order)}</div>
</div>

<%include file="company_table.mako"/>