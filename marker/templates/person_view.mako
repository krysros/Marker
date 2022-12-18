<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">
    <ul class="nav nav-pills">
      <li class="nav-item">
        <a class="nav-link active" aria-current="page" href="${request.route_url('person_view', person_id=person.id, slug=person.slug)}">Osoba</a>
      </li>
    </ul>
  </div>
  <div>${button.vcard('person_vcard', person_id=person.id, slug=person.slug)}</div>
  <div>${button.edit('person_edit', person_id=person.id, slug=person.slug)}</div>
  <div>${button.delete('person_delete', person_id=person.id, slug=person.slug)}</div>
</div>

<p class="lead">${person.name}</p>

<div class="card mt-4 mb-4">
  <div class="card-header"><i class="bi bi-person"></i> Osoba</div>
  <div class="card-body">
    <dl>
      <dt>Imię i nazwisko</dt>
      <dd>${person.name}</dd>

      % if person.company:
      <dt>Firma</dt>
      <dd><a href="${request.route_url('company_view', company_id=person.company.id, slug=person.company.slug)}">${person.company.name}</a></dd>
      % endif

      % if person.project:
      <dt>Projekt</dt>
      <dd><a href="${request.route_url('project_view', project_id=person.project.id, slug=person.project.slug)}">${person.project.name}</a></dd>
      % endif

      <dt>Stanowisko</dt>
      <dd>${person.position}</dd>

      <dt>Telefon</dt>
      <dd>${person.phone}</dd>

      <dt>Email</dt>
      <dd><a href="mailto:${person.email}">${person.email}</a></dd>
    </dl>
  </div>
</div>

<div class="card mt-4 mb-4">
  <div class="card-header"><i class="bi bi-clock"></i> Data modyfikacji</div>
  <div class="card-body">
    <p>
      % if person.created_at:
        Utworzono: ${person.created_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if person.created_by:
          przez <a href="${request.route_url('user_view', username=person.created_by.name)}">${person.created_by.name}</a>
        % endif
      % endif
      <br>
      % if person.updated_at:
        Zmodyfikowano: ${person.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if person.updated_by:
          przez <a href="${request.route_url('user_view', username=person.updated_by.name)}">${person.updated_by.name}</a>
        % endif
      % endif
    </p>
  </div>
</div>