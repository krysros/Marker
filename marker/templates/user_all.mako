<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-person-circle"></i> Użytkownicy
  <div class="float-end">
    ${button.search('user_search')}
    ${button.add('user_add')}
  </div>
</h2>

<hr>

<div class="hstack gap-2">
  <div>${dropdown.filter_button('user_all', roles)}</div>
  <div>${dropdown.sort_button('user_all', dropdown_sort)}</div>
  <div>${dropdown.order_button('user_all', dropdown_order)}</div>
</div>

<%include file="user_table.mako"/>