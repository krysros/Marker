<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

% if project.latitude:
<div class="card">
  <div class="card-header"><i class="bi bi-map"></i> Mapa</div>
  <div class="card-body">
    <div class="row">
      <div class="col">
        <div id="map"></div>
      </div>
    </div>
  </div>
</div>
% endif

<div class="card">
  <div class="card-header">
    <div class="row">
      <div class="col-8">
        <ul class="nav nav-tabs card-header-tabs">
          <li class="nav-item">
            <a class="nav-link active" aria-current="page" href="${request.route_url('project_view', project_id=project.id, slug=project.slug)}">Projekt</a>
          </li>
        ##      <li class="nav-item">
        ##        <a class="nav-link" href="${request.route_url('project_comments', project_id=project.id, slug=project.slug)}">
        ##        % if c_comments > 0:
        ##        Komentarze <span class="badge text-bg-warning">${c_comments}</span>
        ##        % else:
        ##        Komentarze <span class="badge text-bg-secondary">0</span>
        ##        % endif
        ##        </a>
        ##      </li>
          <li class="nav-item">
            <a class="nav-link" href="${request.route_url('project_watched', project_id=project.id, slug=project.slug)}">
              % if c_watched > 0:
              Obserwacje <span class="badge text-bg-success">${c_watched}</span></a>
              % else:
              Obserwacje <span class="badge text-bg-secondary">0</span></a>
              % endif
          </li>
          <li class="nav-item">
            <a class="nav-link" href="${request.route_url('project_companies', project_id=project.id, slug=project.slug)}">
              % if c_companies > 0:
              Firmy <span class="badge text-bg-info">${c_companies}</span>
              % else:
              Firmy <span class="badge text-bg-secondary">0</span>
              % endif
            </a>
          </li>
        ##      <li class="nav-item">
        ##        <a class="nav-link" href="${request.route_url('project_similar', project_id=project.id, slug=project.slug)}">
        ##          % if c_similar > 0:
        ##          Podobne <span class="badge text-bg-dark">${c_simiar}</span></a>
        ##          % else:
        ##          Podobne <span class="badge text-bg-secondary">0</span></a>
        ##          % endif
        ##        </a>
        ##      </li>
        </ul>
      </div>
      <div class="col-4">
        <div class="float-end">
        <button hx-post="${request.route_url('project_watch', project_id=project.id)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-target="#watch" class="btn btn-sm btn-primary">
          <div id="watch">
          % if project in request.identity.watched:
            <i class="bi bi-eye-fill"></i>
          % else:
            <i class="bi bi-eye"></i>
          % endif
          </div>
        </button>
        ${button.edit('project_edit', project_id=project.id, slug=project.slug)}
        ${button.delete('project_delete', project_id=project.id, slug=project.slug)}
      </div>
      </div>
    </div>
  </div>
  <div class="card-body">
    <dl class="dl-horizontal">
      <dt>Nazwa</dt>
      <dd>${project.name}</dd>
      <dt>Adres</dt>
      <dd>
        ${project.street}<br>
        % if project.postcode:
        ${project.postcode} ${project.city}<br>
        % else:
        ${project.city}<br>
        % endif
        ${states.get(project.state)}<br>
      </dd>
      <dt>Termin</dt>
      % if project.deadline:
      <dd>${project.deadline}</dd>
      % else:
      <dd>---</dd>
      % endif
      <dt>Link</dt>
      <dd><a href="${project.link}" target="_blank">${project.link}</a></dd>
    </dl>
  </div>
</div>

<div class="card">
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
  marker.bindPopup("<b>${project.name}</b><br>${project.street}<br>${project.postcode} ${project.city}<br>${states.get(project.state)}<br><a href=${project.link}>${project.link}</a>").openPopup();
</script>