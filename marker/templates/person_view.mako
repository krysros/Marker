<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card">
  <div class="card-header">
    <i class="bi bi-person"></i> Osoba
  </div>
  <div class="card-body">
    <div class="d-flex">
      <div class="p-2 flex-fill">
        <dl class="dl-horizontal">
          <dt>Imię i nazwisko</dt>
          <dd>${person.name}</dd>

          <dt>Stanowisko</dt>
          <dd>${person.position}</dd>

          <dt>Telefon</dt>
          <dd>${person.phone}</dd>

          <dt>Email</dt>
          <dd><a href="mailto:${person.email}">${person.email}</a></dd>
        </dl>
      </div>
      <div class="p-2">
        ${button.edit('person_edit', person_id=person.id)}
        ${button.danger('person_delete', 'Usuń', person_id=person.id)}
      </div>
    </div>
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="bi bi-clock"></i> Data modyfikacji</div>
  <div class="card-body">
    <p>
      % if person.created_at:
        Utworzono: ${person.created_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if person.created_by:
          przez <a href="${request.route_url('user_view', username=person.created_by.name, what='info')}">${person.created_by.name}</a>
        % endif
      % endif
      <br>
      % if person.updated_at:
        Zmodyfikowano: ${person.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if person.updated_by:
          przez <a href="${request.route_url('user_view', username=person.updated_by.name, what='info')}">${person.updated_by.name}</a>
        % endif
      % endif
    </p>
  </div>
</div>