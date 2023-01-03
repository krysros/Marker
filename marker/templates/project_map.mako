<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2><i class="bi bi-briefcase"></i> Projekty
  <div class="float-end">
    ${button.table('project_all', _query=search_query)}
    ${button.search('project_search')}
    ${button.add('project_add')}
  </div>
</h2>
<hr>
<div id="map"></div>

<%include file="markers.mako"/>