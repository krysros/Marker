<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<%!
  import pycountry
%>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(company_pills)}</div>
  <div>${button.company_star(company)}</div>
  <div>${button.a_button(icon='pencil-square', color='warning', url=request.route_url('company_edit', company_id=company.id, slug=company.slug))}</div>
  <div>${button.button(icon='trash', color='danger', url=request.route_url('company_delete', company_id=company.id, slug=company.slug))}</div>
</div>

<%include file="company_lead.mako"/>

% if company.latitude:
<div id="map"></div>
% endif

<div class="card mt-4 mb-4">
  <div class="card-header">
    <i class="bi bi-buildings"></i> ${_("Company")}
  </div>
  <div class="card-body">
    <div class="row">
      <div class="col">
        <dl>
          <dt>${_("Name")}</dt>
          <dd>${company.name}</dd>
          <dt>${_("Street")}</dt>
          <dd>${company.street or "---"}</dd>
          <dt>${_("Post code")}</dt>
          <dd>${company.postcode or "---"}</dd>
          <dt>${_("City")}</dt>
          <dd>${company.city or "---"}</dd>
          <dt>${_("Subdivision")}</dt>
          <dd>${getattr(pycountry.subdivisions.get(code=company.subdivision), "name", "---")}</dd>
          <dt>${_("Country")}</dt>
          <dd>${countries.get(company.country) or "---"}</dd>
          <dt>${_("Website")}</dt>
          % if company.website:
          <dd><a href="${company.website}" target="_blank">${company.website}</a></dd>
          % else:
          <dd>---</dd>
          % endif
        </dl>
      </div>
      % if company.identification_number:
      <div class="col">
        <dl>
          <dt>${_("NIP")}</dt>
          <dd>${company.identification_number.NIP or "---"}</dd>
          <dt>${_("REGON")}</dt>
          <dd>${company.identification_number.REGON or "---"}</dd>
          <dt>${_("KRS")}</dt>
          <dd>${company.identification_number.KRS or "---"}</dd>
          <dt>${_("Court")}</dt>
          <dd>${courts.get(company.identification_number.court) or "---"}</dd>
        </dl>
      </div>
      % endif
    </div>
  </div>
</div>

<div class="card mt-4 mb-4">
  <div class="card-header"><i class="bi bi-clock"></i> ${_("Modification date")}</div>
  <div class="card-body">
    <p>
      ${_("Created at")}: ${company.created_at.strftime('%Y-%m-%d %H:%M:%S')}
      % if company.created_by:
        ${_("by")} <a href="${request.route_url('user_view', username=company.created_by.name)}">${company.created_by.name}</a>
      % endif
      <br>
      % if company.updated_at:
        ${_("Updated at")}: ${company.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if company.updated_by:
        ${_("by")} <a href="${request.route_url('user_view', username=company.updated_by.name)}">${company.updated_by.name}</a>
        % endif
      % endif
    </p>
  </div>
</div>

<script>
  var map = L.map('map').setView([${company.latitude}, ${company.longitude}], 13);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap'
  }).addTo(map);
  var marker = L.marker([${company.latitude}, ${company.longitude}]).addTo(map);
  let title = `<b>${company.name}</b><br>${company.street}<br>${company.city}<br>${company.country}`;
  marker.bindPopup(title);
  marker.openPopup();
</script>