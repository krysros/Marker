<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-buildings"></i> ${_("Selected companies")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a(icon='table', color='secondary', url=request.route_url('user_selected_companies', username=user.name, _query=q))}
    ${button.button(icon='square', color='warning', url=request.route_url('user_clear_selected_companies', username=user.name))}
    ${button.a(icon='download', color='primary', url=request.route_url('user_export_selected_companies', username=user.name, _query=q))}
  </div>
</h2>
<hr>

<div id="map"></div>

<%include file="markers.mako"/>