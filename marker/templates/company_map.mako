<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-buildings"></i> ${_("Companies")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a_button(icon='table', color='secondary', url=request.route_url('company_all', _query=q))}
    ${button.a_button(icon='search', color='primary', url=request.route_url('company_search'))}
    ${button.a_button(icon='plus-lg', color='success', url=request.route_url('company_add'))}
  </div>
</h2>
<hr>
<div id="map"></div>

<%include file="markers.mako"/>