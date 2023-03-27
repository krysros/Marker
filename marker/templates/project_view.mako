<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="nav_pills" file="nav_pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${nav_pills.project_pill(project)}</div>
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