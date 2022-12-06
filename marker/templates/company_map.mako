<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2><i class="bi bi-buildings"></i> Firmy
  <div class="float-end">
    ${button.table('company_all')}
    ${button.search('company_search')}
    ${button.add('company_add')}
  </div>
</h2>
<hr>
<div id="map"></div>

<%include file="markers.mako"/>