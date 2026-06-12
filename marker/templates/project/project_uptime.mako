<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-briefcase"></i> ${_("Projects")}
  <div class="float-end">
    ${button.a(icon='search', color='primary', url=request.route_url('project_search'))}
    ${button.a(icon='plus-lg', color='success', url=request.route_url('project_add'))}
    % if gemini_api_key_set:
    ${button.a(icon='stars', color='info', url=request.route_url('project_add_ai'), title=_("AI Add"))}
    % endif
  </div>
</h2>
<hr>

<div id="main-container" hx-boost="true" hx-target="#main-container" hx-select="#main-container" hx-swap="outerHTML" hx-push-url="true">
<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <%include file="project_filter.mako"/>
  <div class="vr mx-1"></div>
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
  <div class="vr mx-1"></div>
  <%
    matched_route_name = getattr(request, "matched_route", None).name if getattr(request, "matched_route", None) else ""
  %>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}" hx-boost="false">
    <a class="btn btn-outline-primary" href="${request.route_url('project_all', _query=q)}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('project_map', _query=q)}"><i class="bi bi-map"></i> ${_("Map")}</a>
  </div>
  <div class="vr mx-1"></div>
  ${button.dropdown_quality(
    uptime_url=request.route_url('project_uptime', _query=q),
    duplicates_url=request.route_url('project_duplicates_all', _query=q),
    nolocation_url=request.route_url('project_nolocation', _query=q),
    is_uptime=matched_route_name == 'project_uptime',
    is_duplicates=matched_route_name == 'project_duplicates_all',
    is_nolocation=matched_route_name == 'project_nolocation'
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
    <%include file="project_uptime_rows.mako"/>
  </tbody>
</table>
</div>
</div>
