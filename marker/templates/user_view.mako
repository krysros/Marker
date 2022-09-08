<%include file="navbar.mako"/>
<%namespace name="modal" file="modal.mako"/>

<div class="card">
  <div class="card-body">
    <div class="float-end">
      <a class="btn btn-warning" role="button" href="#top" hx-get="${request.route_url('user_edit', username=user.name)}" hx-target="#main-container">Edytuj</a>
      ${modal.danger_dialog('user_delete', 'Usuń', 'Czy na pewno chcesz usunąć użytkownika z bazy danych?', username=user.name)}
    </div>
  </div>
</div>

<div class="card">
  <div class="card-header">
    <i class="bi bi-person-circle"></i> Użytkownik
  </div>
  <div class="card-body">
    <dl class="row">
      <dt class="col-sm-2">Nazwa użytkownika</dt>
      <dd class="col-sm-10">${user.name}</dd>

      <dt class="col-sm-2">Imię i nazwisko</dt>
      <dd class="col-sm-10">${user.fullname}</dd>

      <dt class="col-sm-2">Email</dt>
      <dd class="col-sm-10"><a href="mailto:${user.email}">${user.email}</a></dd>

      <dt class="col-sm-2">Rola</dt>
      <dd class="col-sm-10">${user.role}</dd>
    </dl>
  </div>
  <div class="card-footer">
    <ul class="nav">
      <li class="nav-item">
        <a class="nav-link" role="button" href="#top" hx-get="${request.route_url('user_comments', username=user.name)}" hx-target="#main-container">Komentarze</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" role="button" href="#top" hx-get="${request.route_url('user_tags', username=user.name)}" hx-target="#main-container">Tagi</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" role="button" href="#top" hx-get="${request.route_url('user_companies', username=user.name)}" hx-target="#main-container">Firmy</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" role="button" href="#top" hx-get="${request.route_url('user_projects', username=user.name)}" hx-target="#main-container">Projekty</a>
      </li>
    </ul>
  </div>
</div>