<%include file="navbar.mako"/>
<%namespace name="modal" file="modal.mako"/>

<div class="card">
  <div class="card-body">
    <div class="float-end">
      <a class="btn btn-warning" role="button" href="#top" hx-get="${request.route_url('person_edit', person_id=person.id)}"  hx-target="#main-container">Edytuj</a>
      ${modal.danger_dialog('person_delete', 'Usuń', 'Czy na pewno chcesz usunąć osobę z bazy danych?', person_id=person.id)}
    </div>
  </div>
</div>

<div class="card">
  <div class="card-header">
    <i class="bi bi-person"></i> Osoba
  </div>
  <div class="card-body">
    <dl class="row">
      <dt class="col-sm-2">Imię i nazwisko</dt>
      <dd class="col-sm-10">${person.name}</dd>

      <dt class="col-sm-2">Stanowisko</dt>
      <dd class="col-sm-10">${person.position}</dd>

      <dt class="col-sm-2">Telefon</dt>
      <dd class="col-sm-10">${person.phone}</dd>

      <dt class="col-sm-2">Email</dt>
      <dd class="col-sm-10"><a href="mailto:${person.email}">${person.email}</a></dd>
    </dl>
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="bi bi-clock"></i> Data modyfikacji</div>
  <div class="card-body">
    <p>
      % if person.created_at:
        Utworzono: ${person.created_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if person.created_by:
          przez <a href="#top" hx-get="${request.route_url('user_view', username=person.created_by.name, what='info')}" hx-target="#main-container">${person.created_by.name}</a>
        % endif
      % endif
      <br>
      % if person.updated_at:
        Zmodyfikowano: ${person.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if person.updated_by:
          przez <a href="#top" hx-get="${request.route_url('user_view', username=person.updated_by.name, what='info')}" hx-target="#main-container">${person.updated_by.name}</a>
        % endif
      % endif
    </p>
  </div>
</div>