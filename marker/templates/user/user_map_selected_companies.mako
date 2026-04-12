<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-buildings"></i> ${_("Selected companies")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a(icon='table', color='secondary', url=request.route_url('user_selected_companies', username=user.name, _query=q))}
    ${button.dropdown_download(url_xlsx=request.route_url('user_export_selected_companies', username=user.name, _query=q), url_ods=request.route_url('user_export_selected_companies', username=user.name, _query={**q, 'format': 'ods'}))}
  </div>
</h2>
<hr>

<div id="map"></div>

<%include file="markers.mako"/>