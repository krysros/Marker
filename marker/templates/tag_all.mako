<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-tags"></i> Tagi
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.search('tag_search')}
    ${button.add('tag_add')}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <div>${dropdown.sort_button('tag_all', dropdown_sort)}</div>
  <div>${dropdown.order_button('tag_all', dropdown_order)}</div>
</div>

<%include file="tag_table.mako"/>