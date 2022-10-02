<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card border-0">
  <div class="row">
    <div class="col">
      ${dropdown.filter_button('user_all', roles)}
      ${dropdown.sort_button('user_all', dropdown_sort)}
      ${dropdown.order_button('user_all', dropdown_order)}
      <div class="float-end">
        ${button.search('user_search')}
        ${button.add('user_add')}
      </div>
    </div>
  </div>
</div>

<%include file="user_table.mako"/>