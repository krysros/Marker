<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card border-0">
  <div class="row">
    <div class="col-3">
      <ul class="nav nav-pills">
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('project_all')}">Tabela</a>
        </li>
        <li class="nav-item">
          <a class="nav-link active" aria-current="page" href="${request.route_url('project_map')}">Mapa</a>
        </li>
      </ul>
    </div>
    <div class="col-9">
      <div class="float-end">
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