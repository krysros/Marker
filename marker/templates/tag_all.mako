<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card">
  <div class="card-body">
    ${dropdown.sort_button('tag_all', dropdown_sort)}
    ${dropdown.order_button('tag_all', dropdown_order)}
    <div class="float-end">
      ${button.search('tag_search')}
      ${button.add('tag_add')}
    </div>
  </div>
</div>

<%include file="tag_table.mako"/>