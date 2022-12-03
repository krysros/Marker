<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="hstack gap-2">
  <div class="me-auto">
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
  <div>${button.table('tag_companies', tag_id=tag.id, slug=tag.slug)}</div>
</div>

<p class="lead">${tag.name}</p>

<div id="map"></div>

<%include file="markers.mako"/>