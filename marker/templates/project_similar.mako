<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">
    <ul class="nav nav-pills">
      <li class="nav-item">
        <a class="nav-link" aria-current="page" href="${request.route_url('project_view', project_id=project.id, slug=project.slug)}">Projekt</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('project_companies', project_id=project.id, slug=project.slug)}">
          Firmy <span class="badge text-bg-secondary">${project.count_companies}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('project_tags', project_id=project.id, slug=project.slug)}">
          Tagi <span class="badge text-bg-secondary">${project.count_tags}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('project_contacts', project_id=project.id, slug=project.slug)}">
          Kontakty <span class="badge text-bg-secondary">${project.count_contacts}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('project_comments', project_id=project.id, slug=project.slug)}">
        Komentarze <span class="badge text-bg-secondary">${project.count_comments}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('project_watched', project_id=project.id, slug=project.slug)}">
          Obserwacje <span class="badge text-bg-secondary"><div id="project-watched-counter" hx-get="${request.route_url('count_project_watched', project_id=project.id, slug=project.slug)}" hx-trigger="watchedProjectEvent from:body">${project.count_watched}</div></span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link active" href="${request.route_url('project_similar', project_id=project.id, slug=project.slug)}">
          Podobne <span class="badge text-bg-secondary">${project.count_similar}</span></a>
        </a>
      </li>
    </ul>
  </div>
</div>

<%include file="project_lead.mako"/>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('project_similar', dd_filter, project_id=project.id, slug=project.slug)}</div>
</div>

<%include file="project_table.mako"/>