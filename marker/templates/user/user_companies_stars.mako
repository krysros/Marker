<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0">
    <i class="bi bi-buildings"></i> ${_("Companies marked with a star")}
    <span class="badge bg-secondary">${counter}</span>
  </h2>
  <div class="d-flex flex-wrap gap-2 justify-content-md-end w-100 w-md-auto">
    ${button.a(icon='map', color='secondary', url=request.route_url('user_map_companies_stars', username=user.name))}
    ${button.button(icon='star', color='warning', url=request.route_url('user_clear_companies_stars', username=user.name))}
    ${button.a(icon='download', color='primary', url=request.route_url('user_export_companies_stars', username=user.name, _query=q))}
  </div>
</div>
<hr>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <%include file="company_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="company_table.mako"/>
