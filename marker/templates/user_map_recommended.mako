<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-hand-thumbs-up"></i> ${_("Recommended")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a_button(icon='table', color='secondary', url=request.route_url('user_recommended', username=user.name))}
    ${button.button(icon='hand-thumbs-up', color='warning', url=request.route_url('user_clear_recommended', username=user.name))}
    ${button.a_button(icon='download', color='primary', url=request.route_url('user_export_recommended', username=user.name, _query=q))}
  </div>
</h2>
<hr>

<div id="map"></div>

<%include file="markers.mako"/>