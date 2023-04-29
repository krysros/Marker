<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(user_pills, active_url=request.route_url('user_companies', username=user.name))}</div>
  <div>${button.a_button(icon='table', color='secondary', url=request.route_url('user_companies', username=user.name))}</div>
</div>

<p class="lead">${user.fullname}</p>

<div id="map"></div>

<%include file="markers.mako"/>