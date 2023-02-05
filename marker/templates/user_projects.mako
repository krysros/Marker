<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">
    <ul class="nav nav-pills">
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('user_view', username=user.name)}">Użytkownik</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('user_companies', username=user.name)}">Firmy <span class="badge text-bg-secondary">${user.count_companies}</span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link active" aria-current="page" href="${request.route_url('user_projects', username=user.name)}">Projekty <span class="badge text-bg-secondary">${user.count_projects}</span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('user_tags', username=user.name)}">Tagi <span class="badge text-bg-secondary">${user.count_tags}</span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('user_contacts', username=user.name)}">Kontakty <span class="badge text-bg-secondary">${user.count_contacts}</span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('user_comments', username=user.name)}">Komentarze <span class="badge text-bg-secondary">${user.count_comments}</span></a>
      </li>
    </ul>
  </div>
</div>

<p class="lead">${user.fullname}</p>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('user_projects', dd_filter, username=user.name)}</div>
  <div>${button.dropdown('user_projects', dd_sort, username=user.name)}</div>
  <div>${button.dropdown('user_projects', dd_order, username=user.name)}</div>
</div>

<%include file="project_table.mako"/>