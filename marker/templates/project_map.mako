<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card border-0">
  <div class="row">
    <div class="col">
      <div class="float-end">
        ${button.table('project_all')}
        ${button.search('project_search')}
        ${button.add('project_add')}
      </div>
    </div>
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="bi bi-briefcase"></i> Projekty</div>
  <div class="card-body">
    <div id="map"></div>
  </div>
</div>

<%include file="markers.mako"/>