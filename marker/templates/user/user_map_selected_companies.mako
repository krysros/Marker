<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-buildings"></i> ${_("Selected companies")}
    <span class="badge bg-secondary">${counter}</span>
  </h2>
  <div class="d-flex flex-wrap gap-2 justify-content-md-end w-100 w-md-auto">
    ${button.a(icon='table', color='secondary', url=request.route_url('user_selected_companies', username=user.name, _query=q))}
    ${button.dropdown_download(url_xlsx=request.route_url('user_export_selected_companies', username=user.name, _query=q), url_ods=request.route_url('user_export_selected_companies', username=user.name, _query={**q, 'format': 'ods'}))}
  </div>
</div>
<hr>

<div id="map"></div>

<%include file="markers.mako"/>