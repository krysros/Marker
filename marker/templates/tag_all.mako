<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>
<%namespace name="button" file="button.mako"/>

<h2><i class="bi bi-tags"></i> Tagi
  <div class="float-end">
    ${button.search('tag_search')}
    ${button.add('tag_add')}
  </div>
</h2>
<hr>

<div class="card border-0">
  <div class="row">
    <div class="col">
      ${dropdown.sort_button('tag_all', dropdown_sort)}
      ${dropdown.order_button('tag_all', dropdown_order)}
    </div>
  </div>
</div>

<%include file="tag_table.mako"/>