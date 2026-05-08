<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-buildings"></i> ${_("Companies marked with a star")}
    <span class="badge bg-secondary">${counter}</span>
  </h2>
  <div class="d-flex flex-wrap gap-2 justify-content-md-end w-100 w-md-auto">
    ${button.button(icon='star', color='warning', url=request.route_url('user_clear_companies_stars', username=user.name))}
    <% from marker.utils.export_columns import company_cols; _export_cols = company_cols(_) %>
    ${button.dropdown_download_cols(request.route_url('user_export_companies_stars', username=user.name), _export_cols)}
  </div>
</div>
<hr>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-outline-primary" href="${request.route_url('user_companies_stars', username=user.name)}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-primary" href="${request.route_url('user_map_companies_stars', username=user.name)}"><i class="bi bi-map"></i> ${_("Map")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_uptime_companies_stars', username=user.name)}"><i class="bi bi-globe"></i> ${_("Uptime")}</a>
  </div>
</div>

<div id="map"></div>

<%include file="markers.mako"/>