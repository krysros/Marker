<%inherit file="layout.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">
    <ul class="nav nav-pills">
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('user_view', username=user.name)}">Użytkownik</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('user_companies', username=user.name)}">Firmy <span class="badge text-bg-secondary">${c_companies}</span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('user_projects', username=user.name)}">Projekty <span class="badge text-bg-secondary">${c_projects}</span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('user_tags', username=user.name)}">Tagi <span class="badge text-bg-secondary">${c_tags}</span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('user_persons', username=user.name)}">Osoby <span class="badge text-bg-secondary">${c_persons}</span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link active" aria-current="page" href="${request.route_url('user_comments', username=user.name)}">Komentarze <span class="badge text-bg-secondary">${c_comments}</span></a>
      </li>
    </ul>
  </div>
</div>

<p class="lead">${user.fullname}</p>

<%include file="comment_more.mako"/>