<%include file="navbar.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card">
  <div class="card-body">
    <div class="float-end">
      ${button.edit('user_edit', username=user.name)}
      ${button.danger('user_delete', 'Usuń', username=user.name)}
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
        <a class="nav-link" role="button" href="#" hx-get="${request.route_url('user_comments', username=user.name)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Komentarze</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" role="button" href="#" hx-get="${request.route_url('user_tags', username=user.name)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Tagi</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" role="button" href="#" hx-get="${request.route_url('user_companies', username=user.name)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Firmy</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" role="button" href="#" hx-get="${request.route_url('user_projects', username=user.name)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Projekty</a>
      </li>
    </ul>
  </div>
</div>