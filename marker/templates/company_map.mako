<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2><i class="bi bi-buildings"></i> ${_("Companies")}
  <div class="float-end">
    ${button.button('company_all', color='secondary', icon='table', _query=search_query)}
    ${button.button('company_search', color='primary', icon='search')}
    ${button.add('company_add')}
  </div>
</h2>
<hr>
<div id="map"></div>

<%include file="markers.mako"/>