<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">
    <ul class="nav nav-pills">
      <li class="nav-item">
        <a class="nav-link active position-relative" aria-current="page" href="${request.route_url('project_view', project_id=project.id, slug=project.slug)}">
          Projekt
          % if project.color != "default":
          <span class="position-absolute top-0 start-100 translate-middle p-2 bg-${project.color} border border-light rounded-circle">
            <span class="visually-hidden">Color</span>
          </span>
          % endif
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('project_companies', project_id=project.id, slug=project.slug)}">
          Firmy <span class="badge text-bg-secondary">${project.count_companies}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('project_tags', project_id=project.id, slug=project.slug)}">
          Tagi <span class="badge text-bg-secondary">${project.count_tags}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('project_contacts', project_id=project.id, slug=project.slug)}">
          Kontakty <span class="badge text-bg-secondary">${project.count_contacts}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('project_comments', project_id=project.id, slug=project.slug)}">
          Komentarze <span class="badge text-bg-secondary">${project.count_comments}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('project_watched', project_id=project.id, slug=project.slug)}">
          Obserwacje <span class="badge text-bg-secondary"><div hx-get="${request.route_url('count_project_watched', project_id=project.id, slug=project.slug)}" hx-trigger="watchedProjectEvent from:body">${project.count_watched}</div></span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('project_similar', project_id=project.id, slug=project.slug)}">
          Podobne <span class="badge text-bg-secondary">${project.count_similar}</span></a>
        </a>
      </li>
    </ul>
  </div>
  <div>${button.watch(project)}</div>
  <div>${button.edit('project_edit', project_id=project.id, slug=project.slug)}</div>
  <div>${button.delete('project_delete', project_id=project.id, slug=project.slug)}</div>
</div>

<%include file="project_lead.mako"/>

% if project.latitude:
<div id="map"></div>
% endif

<div class="card mt-4 mb-4">
  <div class="card-header"><i class="bi bi-briefcase"></i> Projekt</div>
  <div class="card-body">
    <div class="row">
      <div class="col">
        <dl>
          <dt>Nazwa</dt>
          <dd>${project.name}</dd>
          <dt>Ulica</dt>
          <dd>${project.street or "---"}</dd>
          <dt>Kod pocztowy</dt>
          <dd>${project.postcode or "---"}</dd>
          <dt>Miasto</dt>
          <dd>${project.city or "---"}</dd>
          <dt>Region</dt>
          <dd>${regions.get(project.region) or "---"}</dd>
          <dt>Kraj</dt>
          <dd>${countries.get(project.country) or "---"}</dd>      
        </dl>
      </div>
      <div class="col">
        <dl>
          <dt>Link</dt>
          % if project.link:
          <dd><a href="${project.link}" target="_blank">${project.link}</a></dd>
          % else:
          <dd>---</dd>
          % endif
          <dt>Termin</dt>
          <dd>${project.deadline or "---"}</dd>
          <dt>Etap</dt>
          <dd>${stages.get(project.stage) or "---"}</dd>
          <dt>Sposób realizacji</dt>
          <dd>${delivery_methods.get(project.delivery_method) or "---"}</dd>
        </dl>
      </div>
    </div>
  </div>
</div>

<div class="card mt-4 mb-4">
  <div class="card-header"><i class="bi bi-clock"></i> Data modyfikacji</div>
  <div class="card-body">
    <p>
      Utworzono: ${project.created_at.strftime('%Y-%m-%d %H:%M:%S')}
      % if project.created_by:
        przez <a href="${request.route_url('user_view', username=project.created_by.name)}">${project.created_by.name}</a>
      % endif
      <br>
      % if project.updated_at:
        Zmodyfikowano: ${project.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if project.updated_by:
          przez <a href="${request.route_url('user_view', username=project.updated_by.name)}">${project.updated_by.name}</a>
        % endif
      % endif
    </p>
  </div>
</div>

<script>
  var map = L.map('map').setView([${project.latitude}, ${project.longitude}], 13);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap'
  }).addTo(map);
  var marker = L.marker([${project.latitude}, ${project.longitude}]).addTo(map);
  let title = `<b>${project.name}</b><br>Ulica: ${project.street}<br>Miasto: ${project.city}<br>Region: ${project.region}<br>Kraj: ${project.country}`;
  marker.bindPopup(title);
  marker.openPopup();
</script>