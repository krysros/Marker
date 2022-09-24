<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card">
  <div class="card-body">
    ${dropdown.sort_button('person_all', dropdown_sort, sort=sort, order=order)}
    ${dropdown.order_button('person_all', dropdown_order, sort=sort, order=order)}
    <div class="float-end">
      ${button.search('person_search')}
    </div>
  </div>
</div>

<%include file="person_table.mako"/>