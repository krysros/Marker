<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-body">
    <div class="float-right">
      <a href="${request.route_url('user_edit', username=user.username)}" class="btn btn-warning" role="button"><i class="fa fa-edit" aria-hidden="true"></i><div class="d-none d-sm-block"> Edytuj</div></a>
      <button type="button" class="btn btn-danger" data-toggle="modal" data-target="#deleteModal">
        <i class="fa fa-trash" aria-hidden="true"></i><div class="d-none d-sm-block"> Usuń</div>
      </button>
    </div>
  </div>
</div>

<div class="card">
  <div class="card-header">
    <i class="fa fa-user" aria-hidden="true"></i> Użytkownik
  </div>
  <div class="card-body">
    <dl class="row">
      <dt class="col-sm-2">Nazwa użytkownika</dt>
      <dd class="col-sm-10">${user.username}</dd>

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
        <a class="nav-link" href="${request.route_url('user_comments', username=user.username)}">Komentarze</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('user_branches', username=user.username)}">Branże</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('user_companies', username=user.username)}">Firmy</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('user_tenders', username=user.username)}">Przetargi</a>
      </li>
    </ul>
  </div>
</div>

<div class="modal fade" id="deleteModal" tabindex="-1" aria-labelledby="deleteModalLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="deleteModalLabel">Usuń</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        Czy na pewno chcesz usunąć użytkownika z bazy danych?
      </div>
      <div class="modal-footer">
        <form action="${request.route_url('user_delete', username=user.username)}" method="post">
          <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
          <button type="button" class="btn btn-secondary" data-dismiss="modal">Nie</button>
          <button type="submit" class="btn btn-primary" name="submit" value="delete">Tak</button>
        </form>
      </div>
    </div>
  </div>
</div>
