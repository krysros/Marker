<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-people"></i> Osoby
  <div class="float-end">
    ${button.search('person_search')}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <div>${dropdown.sort_button('person_all', dropdown_sort)}</div>
  <div>${dropdown.order_button('person_all', dropdown_order)}</div>
</div>

<%include file="person_table.mako"/>