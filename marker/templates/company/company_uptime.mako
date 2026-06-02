<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-buildings"></i> ${_("Companies")}
  <div class="float-end">
    ${button.a(icon='search', color='primary', url=request.route_url('company_search'))}
    ${button.a(icon='plus-lg', color='success', url=request.route_url('company_add'))}
    % if gemini_api_key_set:
    ${button.a(icon='stars', color='info', url=request.route_url('company_add_ai'), title=_("AI Add"))}
    % endif
  </div>
</h2>
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
    <a class="btn btn-outline-primary" href="${request.route_url('company_all', _query=q)}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('company_map', _query=q)}"><i class="bi bi-map"></i> ${_("Map")}</a>
  </div>
  <div class="vr mx-1"></div>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}" hx-boost="false">
    <a class="btn ${'btn-primary' if matched_route_name == 'company_uptime' else 'btn-outline-primary'}" href="${request.route_url('company_uptime', _query=q)}"><i class="bi bi-globe"></i> ${_("Uptime")}</a>
    <a class="btn ${'btn-primary' if matched_route_name == 'company_duplicates_all' else 'btn-outline-primary'}" href="${request.route_url('company_duplicates_all', _query=q)}"><i class="bi bi-files"></i> ${_("Duplicates")}</a>
    <a class="btn ${'btn-primary' if matched_route_name == 'company_nolocation' else 'btn-outline-primary'}" href="${request.route_url('company_nolocation', _query=q)}"><i class="bi bi-geo"></i> ${_("No location")}</a>
  </div>
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
    <%include file="company_uptime_rows.mako"/>
  </tbody>
</table>
</div>
</div>
