<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2><i class="bi bi-briefcase"></i> ${_("Projects")}
  <div class="float-end">
    ${button.button('project_all', color='secondary', icon='table', _query=search_query)}
    ${button.button('project_search', color='primary', icon='search')}
    ${button.add('project_add')}
  </div>
</h2>
<hr>
<div id="map"></div>

<%include file="markers.mako"/>