<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card border-0">
  <div class="row">
    <div class="col">
      ${dropdown.filter_button('company_all', colors)}
      ${dropdown.sort_button('company_all', dropdown_sort)}
      ${dropdown.order_button('company_all', dropdown_order)}
      <div class="float-end">
        ${button.search('company_search')}
        ${button.add('company_add')}
      </div>
    </div>
  </div>
</div>

<%include file="company_table.mako"/>