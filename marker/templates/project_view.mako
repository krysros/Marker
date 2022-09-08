<%include file="navbar.mako"/>
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
      <a class="btn btn-warning" role="button" href="#top" hx-get="${request.route_url('project_edit', project_id=project.id, slug=project.slug)}" hx-target="#main-container">Edytuj</a>
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
          <dt>Termin</dt>
          % if project.deadline:
          <dd>${project.deadline}</dd>
          % else:
          <dd>---</dd>
          % endif
          <dt>Link</dt>
          <dd><a href="${project.link}" target="_blank">${project.link}</a></dd>
        </dl>
      </div>
    </div>
  </div>
  <div class="card-footer">
    <ul class="nav">
##      <li class="nav-item">
##        % if c_comments:
##        <a class="nav-link text-warning" role="button" href="#top" hx-get="${request.route_url('project_comments', project_id=project.id, slug=project.slug)}" hx-target="#main-container">Komentarze (${c_comments})</a>
##        % else:
##        <a class="nav-link" role="button" href="#top" hx-get="${request.route_url('project_comments', project_id=project.id, slug=project.slug)}" hx-target="#main-container">Komentarze (${c_comments})</a>
##        % endif
##      </li>
##      <li class="nav-item">
##        % if c_watched:
##        <a class="nav-link text-success" role="button" href="#top" hx-get="${request.route_url('project_watched', project_id=project.id, slug=project.slug)}" hx-target="#main-container">Obserwowane (${c_watched})</a>
##        % else:
##        <a class="nav-link" role="button" href="#top" hx-get="${request.route_url('project_watched', project_id=project.id, slug=project.slug)}" hx-target="#main-container">Obserwowane (${c_watched)</a>
##        % endif
##      </li>
      <li class="nav-item">
        <a class="nav-link" role="button" href="#top" hx-get="${request.route_url('project_companies', project_id=project.id, slug=project.slug)}" hx-target="#main-container">Firmy (${c_companies})</a>
      </li>
##      <li class="nav-item">
##        <a class="nav-link" role="button" href="#top" hx-get="${request.route_url('project_similar', project_id=project.id, slug=project.slug)}" hx-target="#main-container">Podobne (${c_similar})</a>
##      </li>
    </ul>
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="bi bi-clock"></i> Data modyfikacji</div>
  <div class="card-body">
    <p>
      Utworzono: ${project.created_at.strftime('%Y-%m-%d %H:%M:%S')}
      % if project.created_by:
        przez <a href="#top" hx-get="${request.route_url('user_view', username=project.created_by.name, what='info')}" hx-target="#main-container">${project.created_by.name}</a>
      % endif
      <br>
      % if project.updated_at:
        Zmodyfikowano: ${project.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if project.updated_by:
          przez <a href="#top" hx-get="${request.route_url('user_view', username=project.updated_by.name, what='info')}" hx-target="#main-container">${project.updated_by.name}</a>
        % endif
      % endif
    </p>
  </div>
</div>

<script>
  // Hide Company Modal
  const modalCompanyEl = document.getElementById("add-company-modal");
  const modalCompany = new bootstrap.Modal(modalCompanyEl);
  document.getElementById("btn-save-company").addEventListener("click", function () {
    modalCompany.hide();
  });
  // Clear input fields in Company Modal
  const btnAddCompany = document.getElementById("btn-add-company");
  btnAddCompany.addEventListener('click', function handleClick(event) {
    const companyName = document.getElementById("company-name");
    companyName.value = '';
  });
</script>