<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card border-0">
  <div class="row">
    <div class="col-9">
      <ul class="nav nav-pills">
        <li class="nav-item">
          <a class="nav-link active" aria-current="page" href="${request.route_url('project_view', project_id=project.id, slug=project.slug)}">Projekt</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('project_companies', project_id=project.id, slug=project.slug)}">
            Firmy <span class="badge text-bg-secondary">${c_companies}</span>
          </a>
        </li>
      ##      <li class="nav-item">
      ##        <a class="nav-link" href="${request.route_url('project_comments', project_id=project.id, slug=project.slug)}">
      ##        Komentarze <span class="badge text-bg-secondary">${c_comments}</span>
      ##        </a>
      ##      </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('project_watched', project_id=project.id, slug=project.slug)}">
            Obserwacje <span class="badge text-bg-secondary"><div id="project-watched-counter" hx-get="${request.route_url('count_project_watched', project_id=project.id, slug=project.slug)}" hx-trigger="watchedProjectEvent from:body">${c_watched}</div></span></a>
        </li>
      ##      <li class="nav-item">
      ##        <a class="nav-link" href="${request.route_url('project_similar', project_id=project.id, slug=project.slug)}">
      ##          Podobne <span class="badge text-bg-secondary">${c_simiar}</span></a>
      ##        </a>
      ##      </li>
      </ul>
    </div>
    <div class="col-3">
      <div class="float-end">
        <button hx-post="${request.route_url('project_watch', project_id=project.id)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-target="#watch" class="btn btn-primary">
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

<div class="card">
  <div class="card-header"><i class="bi bi-briefcase"></i> Projekt</div>
  <div class="card-body">
    % if project.latitude:
    <div id="map"></div>
    <hr>
    % endif
    <div class="row">
      <div class="col">
        <dl>
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
            ${countries.get(project.country)}<br>
          </dd>
          <dt>Link</dt>
          <dd><a href="${project.link}" target="_blank">${project.link}</a></dd>        
        </dl>
      </div>
      <div class="col">
        <dl>
          <dt>Termin</dt>
          % if project.deadline:
          <dd>${project.deadline}</dd>
          % else:
          <dd>---</dd>
          % endif
          <dt>Etap</dt>
          <dd>${stages.get(project.stage)}</dd>
          <dt>Sposób realizacji</dt>
          <dd>${project_delivery_methods.get(project.project_delivery_method)}</dd>
        </dl>
      </div>
    </div>
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
</script>