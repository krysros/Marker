<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-eye"></i> ${_("Watched")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a_button(icon='table', color='secondary', url=request.route_url('user_watched', username=user.name))}
    ${button.button(icon='eye', color='warning', url=request.route_url('user_clear_watched', username=user.name))}
    ${button.a_button(icon='download', color='primary', url=request.route_url('user_export_watched', username=user.name, _query=q))}
  </div>
</h2>
<hr>

<div id="map"></div>

<%include file="markers.mako"/>