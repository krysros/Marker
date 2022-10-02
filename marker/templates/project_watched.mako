<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-header">
    <div class="row">
      <div class="col">
        <ul class="nav nav-tabs card-header-tabs">
          <li class="nav-item">
            <a class="nav-link" href="${request.route_url('project_view', project_id=project.id, slug=project.slug)}">Projekt</a>
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
            <a class="nav-link active" aria-current="page" href="${request.route_url('project_watched', project_id=project.id, slug=project.slug)}">
              Obserwacje <span class="badge text-bg-secondary">${c_watched}</span></a>
          </li>
        ##      <li class="nav-item">
        ##        <a class="nav-link" href="${request.route_url('project_similar', project_id=project.id, slug=project.slug)}">
        ##          Podobne <span class="badge text-bg-secondary">${c_simiar}</span></a>
        ##        </a>
        ##      </li>
        </ul>
      </div>
    </div>
  </div>
  <div class="card-body">
    <p>Projekt <strong>${project.name}</strong> obserwują</p>
  </div>
</div>

<%include file="user_table.mako"/>