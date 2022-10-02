<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card border-0">
  <div class="row">
    <div class="col-9">
      <ul class="nav nav-pills">
        <li class="nav-item">
          <a class="nav-link active" aria-current="page" href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">Firma</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('company_projects', company_id=company.id, slug=company.slug)}">
            Projekty <span class="badge text-bg-secondary">${c_projects}</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('company_tags', company_id=company.id, slug=company.slug)}">
            Tagi <span class="badge text-bg-secondary">${c_tags}</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('company_persons', company_id=company.id, slug=company.slug)}">
            Osoby <span class="badge text-bg-secondary">${c_persons}</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('company_comments', company_id=company.id, slug=company.slug)}">
            Komentarze <span class="badge text-bg-secondary">${c_comments}</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('company_recomended', company_id=company.id, slug=company.slug)}">
            Rekomendacje <span class="badge text-bg-secondary">${c_recomended}</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('company_similar', company_id=company.id, slug=company.slug)}">
            Podobne <span class="badge text-bg-secondary">${c_similar}</span>
          </a>
        </li>
      </ul>
    </div>
    <div class="col-3">
      <div class="float-end">
        <button class="btn btn-primary" hx-post="${request.route_url('company_recommend', company_id=company.id)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-target="#recomended">
          <div id="recomended">
            % if company in request.identity.recomended:
              <i class="bi bi-hand-thumbs-up-fill"></i>
            % else:
              <i class="bi bi-hand-thumbs-up"></i>
            % endif
          </div>
        </button>
        ${button.edit('company_edit', company_id=company.id, slug=company.slug)}
        ${button.delete('company_delete', company_id=company.id, slug=company.slug)}
      </div>
    </div>
  </div>
</div>

<div class="card border-${company.color}">
  <div class="card-header">
    <div class="form-check">
      % if company in request.identity.checked:
      <input class="form-check-input"
            id="mark"
            type="checkbox"
            value="${company.id}"
            autocomplete="off"
            checked
            hx-post="${request.route_url('company_check', company_id=company.id)}"
            hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
            hx-trigger="click"
            hx-swap="none">
      % else:
      <input class="form-check-input"
            id="mark"
            type="checkbox"
            value="${company.id}"
            autocomplete="off"
            hx-post="${request.route_url('company_check', company_id=company.id)}"
            hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
            hx-trigger="click"
            hx-swap="none">
      % endif
      <label class="form-check-label" for="mark">${company.name}</label>
    </div>
  </div>
  <div class="card-body">
    % if company.latitude:
    <div id="map"></div>
    <hr>
    % endif
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
          </dd>
          <dt>Link</dt>
          <dd>
          % if company.WWW.startswith('http'):
            <a href="${company.WWW}">
          % else:
            <a href="${'http://' + company.WWW}">
          % endif
            ${company.WWW}</a>
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

<div class="card">
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
</script>