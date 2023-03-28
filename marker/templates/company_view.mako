<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.company_pill(company)}</div>
  <div>${button.recommend(company)}</div>
  <div>${button.edit('company_edit', company_id=company.id, slug=company.slug)}</div>
  <div>${button.delete('company_delete', company_id=company.id, slug=company.slug)}</div>
</div>

<%include file="company_lead.mako"/>

% if company.latitude:
<div id="map"></div>
% endif

<div class="card mt-4 mb-4">
  <div class="card-header">
    <i class="bi bi-buildings"></i> Firma
  </div>
  <div class="card-body">
    <div class="row">
      <div class="col">
        <dl>
          <dt>Nazwa</dt>
          <dd>${company.name}</dd>
          <dt>Ulica</dt>
          <dd>${company.street or "---"}</dd>
          <dt>Kod pocztowy</dt>
          <dd>${company.postcode or "---"}</dd>
          <dt>Miasto</dt>
          <dd>${company.city or "---"}</dd>
          <dt>Region</dt>
          <dd>${regions.get(company.region) or "---"}</dd>
          <dt>Kraj</dt>
          <dd>${countries.get(company.country) or "---"}</dd>
        </dl>
      </div>
      <div class="col">
        <dl>
          <dt>Link</dt>
          % if company.link:
          <dd><a href="${company.link}" target="_blank">${company.link}</a></dd>
          % else:
          <dd>---</dd>
          % endif
          </dd>
          <dt>NIP</dt>
          <dd>${company.NIP or "---"}</dd>
          <dt>REGON</dt>
          <dd>${company.REGON or "---"}</dd>
          <dt>KRS</dt>
          <dd>${company.KRS or "---"}</dd>
          <dt>Sąd</dt>
          <dd>${courts.get(company.court) or "---"}</dd>
        </dl>
      </div>
    </div>
  </div>
</div>

<div class="card mt-4 mb-4">
  <div class="card-header"><i class="bi bi-clock"></i> Data modyfikacji</div>
  <div class="card-body">
    <p>
      Utworzono: ${company.created_at.strftime('%Y-%m-%d %H:%M:%S')}
      % if company.created_by:
        przez <a href="${request.route_url('user_view', username=company.created_by.name)}">${company.created_by.name}</a>
      % endif
      <br>
      % if company.updated_at:
        Zmodyfikowano: ${company.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if company.updated_by:
          przez <a href="${request.route_url('user_view', username=company.updated_by.name)}">${company.updated_by.name}</a>
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
  let title = `<b>${company.name}</b><br>Ulica: ${company.street}<br>Miasto: ${company.city}<br>Region: ${company.region}<br>Kraj: ${company.country}`;
  marker.bindPopup(title);
  marker.openPopup();
</script>