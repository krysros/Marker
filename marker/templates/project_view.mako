<%inherit file="layout.mako"/>
<%namespace name="modal" file="modal.mako"/>

<div class="card">
  <div class="card-body">
    <div class="float-end">
      <button hx-post="${request.route_url('project_watch', project_id=project.id)}" hx-target="#watch" class="btn btn-primary">
        <div id="watch">
        % if project in request.identity.watched:
          <i class="bi bi-eye-fill"></i>
        % else:
          <i class="bi bi-eye"></i>
        % endif
        </div>
      </button>
      <a href="${request.route_url('project_edit', project_id=project.id, slug=project.slug)}" class="btn btn-warning" role="button">Edytuj</a>
      ${modal.danger_dialog('project_delete', 'Usuń', 'Czy na pewno chcesz usunąć projekt z bazy danych?', project_id=project.id, slug=project.slug)}
    </div>
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="bi bi-briefcase"></i> Projekt</div>
  <div class="card-body">
    <div class="row">
      <div class="col">
        <h1>${project.name}</h1>
      </div>
    </div>
    <div class="row">
      <div class="col">
        <dl class="dl-horizontal">
          <dt>Adres</dt>
            <dd>
              ${project.street}<br>
              % if project.postcode:
              ${project.postcode} ${project.city}<br>
              % else:
              ${project.city}<br>
              % endif
              ${states.get(project.state)}<br>
            </dd>
          <dt>Firma</dt>
            % if project.company:
            <dd><a href="${request.route_url('company_view', company_id=project.company.id, slug=project.company.slug)}">${project.company.name}</a></dd>
            % else:
            <dd>---</dd>
            % endif
          <dt>Termin</dt>
          <dd>${project.deadline}</dd>
          <dt>Link</dt>
          <dd><a href="${project.link}" target="_blank">${project.link}</a></dd>
        </dl>
      </div>
    </div>
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="bi bi-clock"></i> Data modyfikacji</div>
  <div class="card-body">
    <p>
      Utworzono: ${project.created_at.strftime('%Y-%m-%d %H:%M:%S')}
      % if project.created_by:
        przez <a href="${request.route_url('user_view', username=project.created_by.name, what='info')}">${project.created_by.name}</a>
      % endif
      <br>
      % if project.updated_at:
        Zmodyfikowano: ${project.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if project.updated_by:
          przez <a href="${request.route_url('user_view', username=project.updated_by.name, what='info')}">${project.updated_by.name}</a>
        % endif
      % endif
    </p>
  </div>
</div>