<%inherit file="layout.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">
    <ul class="nav nav-pills">
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

<div class="hstack">
  <div class="me-auto">
    <p class="lead">${project.name}</p>
  </div>
  % if project.color != "default":
  <div>
    <p class="lead"><i class="bi bi-circle-fill text-${project.color}"></i></p>
  </div>
  % endif
</div>

<%include file="user_table.mako"/>