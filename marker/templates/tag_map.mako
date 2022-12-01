<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card border-0">
  <div class="row">
    <div class="col-9">
      <ul class="nav nav-pills">
        <li class="nav-item">
          <a class="nav-link" aria-current="page" href="${request.route_url('tag_view', tag_id=tag.id, slug=tag.slug)}">Tag</a>
        </li>
        <li class="nav-item">
          <a class="nav-link active" href="${request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug)}">
            Firmy <span class="badge text-bg-secondary">${c_companies}</span>
          </a>
        </li>
      </ul>
    </div>
    <div class="col-3">
      <div class="float-end">
        ${button.table('tag_companies', tag_id=tag.id, slug=tag.slug)}   
      </div>
    </div>
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="bi bi-building"></i> Firmy</div>
  <div class="card-body">
    <div id="map"></div>
  </div>
</div>

<%include file="markers.mako"/>