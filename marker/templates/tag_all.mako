<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-tags"></i> Tagi
  <small class="text-muted">${heading}</small>
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.search('tag_search')}
    ${button.add('tag_add')}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('tag_all', dd_sort)}</div>
  <div>${button.dropdown('tag_all', dd_order)}</div>
</div>

<%include file="tag_table.mako"/>