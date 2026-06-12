<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-buildings"></i> ${_("Selected companies")}
  </h2>
  <div class="d-flex flex-wrap gap-2 justify-content-md-end w-100 w-md-auto">
    ${button.deselect_selected(url=request.route_url('user_deselect_companies', username=user.name), confirm_text=_("Deselect all selected companies?"))}
    ${button.delete_selected(url=request.route_url('user_delete_selected_companies', username=user.name), confirm_text=_("Delete all selected companies?"))}
  </div>
</div>
<hr>

<div id="main-container" hx-boost="true" hx-target="#main-container" hx-select="#main-container" hx-swap="outerHTML" hx-push-url="true">
<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <%include file="company_filter.mako"/>
  <div class="vr mx-1"></div>
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
  <div class="vr mx-1"></div>
  <%
    matched_route_name = getattr(request, "matched_route", None).name if getattr(request, "matched_route", None) else ""
  %>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}" hx-boost="false">
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_companies', username=user.name, _query=q)}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_map_selected_companies', username=user.name, _query=q)}"><i class="bi bi-map"></i> ${_("Map")}</a>
  </div>
  <div class="vr mx-1"></div>
  ${button.dropdown_quality(
    uptime_url=request.route_url('user_uptime_selected_companies', username=user.name, _query=q),
    duplicates_url=request.route_url('user_duplicates_selected_companies', username=user.name, _query=q),
    nolocation_url=request.route_url('user_nolocation_selected_companies', username=user.name, _query=q),
    is_uptime=matched_route_name == 'user_uptime_selected_companies',
    is_duplicates=matched_route_name == 'user_duplicates_selected_companies',
    is_nolocation=matched_route_name == 'user_nolocation_selected_companies'
  )}
</div>

<%include file="search_criteria.mako"/>

<div class="table-responsive">
<table class="table table-striped">
  <thead>
    <tr>
      <th>#</th>
      <th>${_("Name")}</th>
      <th>${_("Website")}</th>
      <th>${_("HTTP response code")}</th>
    </tr>
  </thead>
  <tbody id="uptime-tbody">
    <%include file="user_uptime_selected_companies_rows.mako"/>
  </tbody>
</table>
</div>
</div>
