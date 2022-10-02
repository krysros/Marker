<%inherit file="layout.mako"/>

<div class="card border-${company.color}">
  <div class="card-header">
    <ul class="nav nav-tabs card-header-tabs">
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">Firma</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_projects', company_id=company.id, slug=company.slug)}">
          Projekty <span class="badge text-bg-secondary">${c_projects}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_persons', company_id=company.id, slug=company.slug)}">
          Osoby <span class="badge text-bg-secondary">${c_persons}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_tags', company_id=company.id, slug=company.slug)}">
          Tagi <span class="badge text-bg-secondary">${c_tags}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_comments', company_id=company.id, slug=company.slug)}">
          Komentarze <span class="badge text-bg-secondary">${c_comments}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link active" aria-current="page" href="${request.route_url('company_recomended', company_id=company.id, slug=company.slug)}">
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
  <div class="card-body">
    <p>Firmę <strong>${company.name}</strong> rekomendują</p>
  </div>
</div>

<%include file="user_table.mako"/>