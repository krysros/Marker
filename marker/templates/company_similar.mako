<%inherit file="layout.mako"/>
<%namespace name="dropdown" file="dropdown.mako"/>

<div class="card border-0">
  <div class="row">
    <div class="col-9">
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
    <div class="col-3">
      <div class="float-end">
        ${dropdown.filter_button('company_similar', states, company_id=company.id, slug=company.slug)}
      </div>
    </div>
  </div>
</div>

<%include file="company_table.mako"/>