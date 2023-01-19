<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">
    <ul class="nav nav-pills">
      <li class="nav-item">
        <a class="nav-link active position-relative" aria-current="page" href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">
          Firma
          % if company.color != "default":
          <span class="position-absolute top-0 start-100 translate-middle p-2 bg-${company.color} border border-light rounded-circle">
            <span class="visually-hidden">Color</span>
          </span>
          % endif
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_projects', company_id=company.id, slug=company.slug)}">
          Projekty <span class="badge text-bg-secondary">${company.count_projects}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_tags', company_id=company.id, slug=company.slug)}">
          Tagi <span class="badge text-bg-secondary">${company.count_tags}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_persons', company_id=company.id, slug=company.slug)}">
          Osoby <span class="badge text-bg-secondary">${company.count_persons}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_comments', company_id=company.id, slug=company.slug)}">
          Komentarze <span class="badge text-bg-secondary">${company.count_comments}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_recommended', company_id=company.id, slug=company.slug)}">
          Rekomendacje <span class="badge text-bg-secondary"><div id="company-recommended-counter" hx-get="${request.route_url('count_company_recommended', company_id=company.id, slug=company.slug)}" hx-trigger="recommendedCompanyEvent from:body">${company.count_recommended}</div></span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_similar', company_id=company.id, slug=company.slug)}">
          Podobne <span class="badge text-bg-secondary">${company.count_similar}</span>
        </a>
      </li>
    </ul>
  </div>
  <div>
    <button class="btn btn-primary" hx-post="${request.route_url('company_recommend', company_id=company.id)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-target="#recommended">
      <div id="recommended">
        % if company in request.identity.recommended:
          <i class="bi bi-hand-thumbs-up-fill"></i>
        % else:
          <i class="bi bi-hand-thumbs-up"></i>
        % endif
      </div>
    </button>
  </div>
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
          <dt>Adres</dt>
          <dd>
            ${company.street}<br>
            % if company.postcode:
            ${company.postcode} ${company.city}<br>
            % else:
            ${company.city}<br>
            % endif
            ${states.get(company.state)}<br>
            ${countries.get(company.country)}<br>
          </dd>
          <dt>Link</dt>
          <dd>
          % if company.link.startswith('http'):
            <a href="${company.link}">
          % else:
            <a href="${'http://' + company.link}">
          % endif
            ${company.link}</a>
          </dd>      
        </dl>
      </div>
      <div class="col">
        <dl>
          <dt>Dane rejestrowe</dt>
          <dd>
            NIP: ${company.NIP or "brak"}<br>
            REGON: ${company.REGON or "brak"}<br>
            KRS: ${company.KRS or "brak"}
            % if company.court:
              <br>${courts.get(company.court)}
            % endif
          </dd>
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
  let title = `<b>${company.name}</b><br>Ulica: ${company.street}<br>Miasto: ${company.city}<br>Woj.: ${company.state}<br>Kraj: ${company.country}`;
  marker.bindPopup(title);
  marker.openPopup();
</script>