<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">
    <ul class="nav nav-pills">
      <li class="nav-item">
        <a class="nav-link active" aria-current="page" href="${request.route_url('user_view', username=user.name)}">Użytkownik</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('user_companies', username=user.name)}">Firmy <span class="badge text-bg-secondary">${user.count_companies}</span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('user_projects', username=user.name)}">Projekty <span class="badge text-bg-secondary">${user.count_projects}</span></a>
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
  <div>${button.edit('user_edit', username=user.name)}</div>
  <div>${button.delete('user_delete', username=user.name)}</div>
</div>

<p class="lead">${user.fullname}</p>

<div class="card mt-4 mb-4">
  <div class="card-header"><i class="bi bi-person-circle"></i> Użytkownik</div>
  <div class="card-body">
    <dl>
      <dt>Nazwa</dt>
      <dd>${user.name}</dd>

      <dt>Imię i nazwisko</dt>
      <dd>${user.fullname or "---"}</dd>

      <dt>Email</dt>
      % if user.email:
      <dd><a href="mailto:${user.email}">${user.email}</a></dd>
      % else:
      <dd>---</dd>
      % endif

      <dt>Rola</dt>
      <dd>${user.role or "---"}</dd>
    </dl>
  </div>
</div>

<div class="card mt-4 mb-4">
  <div class="card-header"><i class="bi bi-clock"></i> Data modyfikacji</div>
  <div class="card-body">
    <p>
      Utworzono: ${user.created_at.strftime('%Y-%m-%d %H:%M:%S')}
      <br>
      % if user.updated_at:
        Zmodyfikowano: ${user.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
      % endif
    </p>
  </div>
</div>