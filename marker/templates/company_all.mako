<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card">
  <div class="card-body">
    ${dropdown.filter_button('company_all', colors, filter=filter, sort=sort, order=order)}
    ${dropdown.sort_button('company_all', dropdown_sort, filter=filter, sort=sort, order=order)}
    ${dropdown.order_button('company_all', dropdown_order, filter=filter, sort=sort, order=order)}
    <div class="float-end">
      ${button.search('company_search')}
      ${button.add('company_add')}
    </div>
  </div>
</div>

<%include file="company_table.mako"/>