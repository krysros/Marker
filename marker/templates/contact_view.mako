<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">
    <ul class="nav nav-pills">
      <li class="nav-item">
        <a class="nav-link active" aria-current="page" href="${request.route_url('contact_view', contact_id=contact.id, slug=contact.slug)}">Kontakt</a>
      </li>
    </ul>
  </div>
  <div>${button.vcard('contact_vcard', contact_id=contact.id, slug=contact.slug)}</div>
  <div>${button.edit('contact_edit', contact_id=contact.id, slug=contact.slug)}</div>
  <div>${button.delete('contact_delete', contact_id=contact.id, slug=contact.slug)}</div>
</div>

<p class="lead">${contact.name}</p>

<div class="card mt-4 mb-4">
  <div class="card-header"><i class="bi bi-person"></i> Kontakt</div>
  <div class="card-body">
    <dl>
      <dt>Imię i nazwisko</dt>
      <dd>${contact.name}</dd>

      % if contact.company:
      <dt>Firma</dt>
      <dd><a href="${request.route_url('company_view', company_id=contact.company.id, slug=contact.company.slug)}">${contact.company.name}</a></dd>
      % endif

      % if contact.project:
      <dt>Projekt</dt>
      <dd><a href="${request.route_url('project_view', project_id=contact.project.id, slug=contact.project.slug)}">${contact.project.name}</a></dd>
      % endif

      <dt>Rola</dt>
      <dd>${contact.role or "---"}</dd>

      <dt>Telefon</dt>
      <dd>${contact.phone or "---"}</dd>

      <dt>Email</dt>
      % if contact.email:
      <dd><a href="mailto:${contact.email}">${contact.email}</a></dd>
      % else:
      <dd>---</dd>
      % endif
    </dl>
  </div>
</div>

<div class="card mt-4 mb-4">
  <div class="card-header"><i class="bi bi-clock"></i> Data modyfikacji</div>
  <div class="card-body">
    <p>
      % if contact.created_at:
        Utworzono: ${contact.created_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if contact.created_by:
          przez <a href="${request.route_url('user_view', username=contact.created_by.name)}">${contact.created_by.name}</a>
        % endif
      % endif
      <br>
      % if contact.updated_at:
        Zmodyfikowano: ${contact.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if contact.updated_by:
          przez <a href="${request.route_url('user_view', username=contact.updated_by.name)}">${contact.updated_by.name}</a>
        % endif
      % endif
    </p>
  </div>
</div>