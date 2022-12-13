<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-buildings"></i> Firmy
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.map('company_map')}
    ${button.search('company_search')}
    ${button.add('company_add')}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('company_all', items=dropdown_sort, criterion=sort, typ='sort', title='Sortuj')}</div>
  <div>${button.dropdown('company_all', items=dropdown_order, criterion=order, typ='order', title='Kolejność')}</div>
</div>

<%include file="company_table.mako"/>