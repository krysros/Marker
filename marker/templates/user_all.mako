<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card">
  <div class="card-body">
    ${dropdown.filter_button('user_all', roles, filter=filter, sort=sort, order=order)}
    ${dropdown.sort_button('user_all', dropdown_sort, filter=filter, sort=sort, order=order)}
    ${dropdown.order_button('user_all', dropdown_order, filter=filter, sort=sort, order=order)}
    <div class="float-end">
      ${button.search('user_search')}
      ${button.add('user_add')}
    </div>
  </div>
</div>

<%include file="user_table.mako"/>