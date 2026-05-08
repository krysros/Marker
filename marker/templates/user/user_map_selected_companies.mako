<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-buildings"></i> ${_("Selected companies")}
    <span class="badge bg-secondary">${counter}</span>
  </h2>
  <div class="d-flex flex-wrap gap-2 justify-content-md-end w-100 w-md-auto">
    ${button.deselect_selected(url=request.route_url('user_deselect_companies', username=user.name), confirm_text=_("Deselect all selected companies?"))}
    ${button.delete_selected(url=request.route_url('user_delete_selected_companies', username=user.name, _query=q), confirm_text=_("Delete all selected companies?"))}
    <% from marker.utils.export_columns import company_cols; _export_cols = company_cols(_) %>
    ${button.dropdown_download_cols(request.route_url('user_export_selected_companies', username=user.name, _query=q), _export_cols)}
  </div>
</div>
<hr>

<div class="d-flex flex-nowrap overflow-x-auto align-items-center gap-2 mb-4 pb-1">
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_companies', username=user.name, _query=q)}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-primary" href="${request.route_url('user_map_selected_companies', username=user.name, _query=q)}"><i class="bi bi-map"></i> ${_("Map")}</a>
  </div>
</div>

<div id="map"></div>

<%include file="markers.mako"/>