<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>
<%! from marker.utils.export_columns import company_cols %>
<% _export_cols = company_cols(_) %>
<div class="d-flex flex-nowrap overflow-x-auto align-items-center gap-2 mb-4 pb-1">
  <div class="me-auto">${pills.pills(user_pills, active_url=request.route_url('user_companies', username=user.name))}</div>
  <div>${button.dropdown_download_cols(request.route_url('user_export_companies', username=user.name, _query=q), _export_cols)}</div>
</div>

<p class="lead">${user.fullname}</p>

<div class="d-flex flex-nowrap overflow-x-auto align-items-center gap-2 mb-4 pb-1">
  <%include file="company_filter.mako"/>
  <div class="vr mx-1"></div>
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
  <div class="vr mx-1"></div>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-primary" href="${request.route_url('user_companies', username=user.name, _query=q)}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_map_companies', username=user.name, _query=q)}"><i class="bi bi-map"></i> ${_("Map")}</a>
  </div>
</div>

<%include file="search_criteria.mako"/>

<%include file="company_table.mako"/>