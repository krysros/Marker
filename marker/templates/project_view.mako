<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.project_pill(project)}</div>
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
          <dt>${_("Name")}</dt>
          <dd>${project.name}</dd>
          <dt>${_("Street")}</dt>
          <dd>${project.street or "---"}</dd>
          <dt>${_("Post code")}</dt>
          <dd>${project.postcode or "---"}</dd>
          <dt>${_("City")}</dt>
          <dd>${project.city or "---"}</dd>
          <dt>${_("Region")}</dt>
          <dd>${regions.get(project.region) or "---"}</dd>
          <dt>${_("Country")}</dt>
          <dd>${countries.get(project.country) or "---"}</dd>      
        </dl>
      </div>
      <div class="col">
        <dl>
          <dt>${_("Link")}</dt>
          % if project.link:
          <dd><a href="${project.link}" target="_blank">${project.link}</a></dd>
          % else:
          <dd>---</dd>
          % endif
          <dt>${_("Deadline")}</dt>
          <dd>${project.deadline or "---"}</dd>
          <dt>${_("Stage")}</dt>
          <dd>${stages.get(project.stage) or "---"}</dd>
          <dt>${_("Project delivery method")}</dt>
          <dd>${delivery_methods.get(project.delivery_method) or "---"}</dd>
        </dl>
      </div>
    </div>
  </div>
</div>

<div class="card mt-4 mb-4">
  <div class="card-header"><i class="bi bi-clock"></i> ${_("Modification date")}</div>
  <div class="card-body">
    <p>
      ${_("Created at")}: ${project.created_at.strftime('%Y-%m-%d %H:%M:%S')}
      % if project.created_by:
        ${_("by")} <a href="${request.route_url('user_view', username=project.created_by.name)}">${project.created_by.name}</a>
      % endif
      <br>
      % if project.updated_at:
        ${_("Updated at")}: ${project.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if project.updated_by:
          ${_("by")} <a href="${request.route_url('user_view', username=project.updated_by.name)}">${project.updated_by.name}</a>
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
  let title = `<b>${project.name}</b><br>${project.street}<br>${project.city}<br>${project.region}<br>${project.country}`;
  marker.bindPopup(title);
  marker.openPopup();
</script>