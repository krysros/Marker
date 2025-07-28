<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-star"></i> ${_("Stars")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a(icon='table', color='secondary', url=request.route_url('user_companies_stars', username=user.name))}
    ${button.button(icon='star', color='warning', url=request.route_url('user_clear_companies_stars', username=user.name))}
    ${button.a(icon='download', color='primary', url=request.route_url('user_export_companies_stars', username=user.name, _query=q))}
  </div>
</h2>
<hr>

<div id="map"></div>

<%include file="markers.mako"/>