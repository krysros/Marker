<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-person-circle"></i> ${_("Users")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a(icon='search', color='primary', url=request.route_url('user_search'))}
    ${button.a(icon='plus-lg', color='success', url=request.route_url('user_add'))}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <%include file="user_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="user_table.mako"/>