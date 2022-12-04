<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">
    <ul class="nav nav-pills">
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">Firma</a>
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
        <a class="nav-link" href="${request.route_url('company_recommended', company_id=company.id, slug=company.slug)}">
          Rekomendacje <span class="badge text-bg-secondary">${c_recommended}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link active" aria-current="page" href="${request.route_url('company_similar', company_id=company.id, slug=company.slug)}">
          Podobne <span class="badge text-bg-secondary">${c_similar}</span>
        </a>
      </li>
    </ul>
  </div>
</div>

<div class="hstack">
  <div class="me-auto">
    <p class="lead">
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
      &nbsp;${company.name}
    </p>
  </div>
  % if company.color != "default":
  <div>
    <p class="lead"><i class="bi bi-circle-fill text-${company.color}"></i></p>
  </div>
  % endif
</div>

<div class="hstack gap-2 mb-4">
  <div>${dropdown.filter_button('company_similar', states, company_id=company.id, slug=company.slug)}</div>
</div>

<%include file="company_table.mako"/>