<%inherit file="layout.mako"/>

<div class="card border-0">
  <div class="row">
    <div class="col-9">
      <ul class="nav nav-pills">
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">Firma</a>
        </li>
        <li class="nav-item">
          <a class="nav-link active" aria-current="page" href="${request.route_url('company_projects', company_id=company.id, slug=company.slug)}">
            Projekty <span class="badge text-bg-secondary">${c_projects}</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('company_tags', company_id=company.id, slug=company.slug)}">
            Tagi <span class="badge text-bg-secondary">${c_tags}</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('company_persons', company_id=company.id, slug=company.slug)}">
            Osoby <span class="badge text-bg-secondary">${c_persons}</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('company_comments', company_id=company.id, slug=company.slug)}">
            Komentarze <span class="badge text-bg-secondary">${c_comments}</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('company_recomended', company_id=company.id, slug=company.slug)}">
            Rekomendacje <span class="badge text-bg-secondary">${c_recomended}</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('company_similar', company_id=company.id, slug=company.slug)}">
            Podobne <span class="badge text-bg-secondary">${c_similar}</span>
          </a>
        </li>
      </ul>
    </div>
    <div class="col-3">
      <div class="float-end">
        % if request.identity.role == 'editor':
        <button id="btn-add-project" type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#add-project-modal">
          Dodaj
        </button>
        % else:
        <button type="button" class="btn btn-success" disabled>Dodaj</button>
        % endif
      </div>
    </div>
  </div>
</div>

<div id="company-projects">
  <%include file="project_list.mako"/>
</div>

<div class="modal fade" id="add-project-modal" tabindex="-1" aria-labelledby="add-project-modal-label" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <form hx-post="${request.route_url('add_project', company_id=company.id, slug=company.slug)}" hx-target="#company-projects" hx-swap="innerHTML show:window:top">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <div class="modal-header">
          <h5 class="modal-title" id="add-project-modal-label">Dodaj projekt</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="project-name" class="form-label">Nazwa</label>
            <input list="projects" type="text" class="form-control" id="project-name" name="name" autocomplete="off" hx-get="${request.route_url('project_select')}" hx-target="#project-list" hx-swap="innerHTML" hx-trigger="keyup changed delay:250ms" required maxlength="200">
            <div id="project-list"></div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zamknij</button>
          <button type="submit" class="btn btn-primary" id="btn-save-project">Zapisz</button>
        </div>
      </form>
    </div>
  </div>
</div>

<script>
  // Hide Project Modal
  var modalProjectEl = document.getElementById("add-project-modal");
  var modalProject = new bootstrap.Modal(modalProjectEl);
  document.getElementById("btn-save-project").addEventListener("click", function () {
    modalProject.hide();
  });
  // Clear input fields in Project Modal
  var btnAddProject = document.getElementById("btn-add-project");
  btnAddProject.addEventListener('click', function handleClick(event) {
    var projectName = document.getElementById("project-name");
    projectName.value = '';
  });
</script> 