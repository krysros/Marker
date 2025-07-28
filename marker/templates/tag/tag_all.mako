<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-tags"></i> ${_("Tags")}
  <span class="badge bg-secondary"><div hx-get="${request.route_url('tag_count')}" hx-trigger="tagEvent from:body">${counter}</div></span>
  <div class="float-end">
    ${button.a(icon='search', color='primary', url=request.route_url('tag_search'))}
    ${button.a(icon='plus-lg', color='success', url=request.route_url('tag_add'))}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="tag_table.mako"/>