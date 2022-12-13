<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-person-circle"></i> Użytkownicy
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.search('user_search')}
    ${button.add('user_add')}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('user_all', items=dropdown_sort, criterion=sort, typ='sort', title='Sortuj')}</div>
  <div>${button.dropdown('user_all', items=dropdown_order, criterion=order, typ='order', title='Kolejność')}</div>
</div>

<%include file="user_table.mako"/>