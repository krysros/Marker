<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-star"></i> ${_("Stars")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a(icon='table', color='secondary', url=request.route_url('user_projects_stars', username=user.name))}
    ${button.button(icon='star', color='warning', url=request.route_url('user_clear_projects_stars', username=user.name))}
    ${button.dropdown_download(url_xlsx=request.route_url('user_export_projects_stars', username=user.name, _query=q), url_ods=request.route_url('user_export_projects_stars', username=user.name, _query={**q, 'format': 'ods'}))}
  </div>
</h2>
<hr>

<div id="map"></div>

<%include file="markers.mako"/>