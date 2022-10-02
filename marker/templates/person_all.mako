<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card border-0">
  <div class="row">
    <div class="col">
      ${dropdown.sort_button('person_all', dropdown_sort)}
      ${dropdown.order_button('person_all', dropdown_order)}
      <div class="float-end">
        ${button.search('person_search')}
      </div>
    </div>
  </div>
</div>

<%include file="person_table.mako"/>