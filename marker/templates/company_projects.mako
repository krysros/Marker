<%inherit file="layout.mako"/>
<%namespace name="nav_pills" file="nav_pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${nav_pills.nav_company(company, active_link="projects")}</div>
  <div>
    % if request.identity.role == 'editor' or 'admin':
    <button id="btn-add-project" type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#add-project-modal">
      <i class="bi bi-plus-lg"></i>
    </button>
    % else:
    <button type="button" class="btn btn-success" disabled><i class="bi bi-plus-lg"></i></button>
    % endif
  </div>
</div>

<%include file="company_lead.mako"/>

<div id="company-projects">
  <%include file="project_list_companies.mako"/>
</div>

<div class="modal fade" id="add-project-modal" tabindex="-1" aria-labelledby="add-project-modal-label" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <form hx-post="${request.route_url('company_add_project', company_id=company.id, slug=company.slug)}" hx-target="#company-projects" hx-swap="innerHTML show:window:top">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <div class="modal-header">
          <h5 class="modal-title" id="add-project-modal-label">Dodaj projekt</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="name" class="form-label">Nazwa</label>
            <input list="projects" type="text" class="form-control" id="name" name="name" autocomplete="off" hx-get="${request.route_url('project_select')}" hx-target="#project-list" hx-swap="innerHTML" hx-trigger="keyup changed delay:250ms" required maxlength="200">
            <div id="project-list"></div>
          </div>
          <div class="mb-3">
            <label for="stage">Etap</label>
            <select class="form-control" id="stage" name="stage">
            % for key, value in stages.items():
              <option value="${key}">${value}</option>
            % endfor
            </select>
          </div>
          <div class="mb-3">
            <label for="role">Rola</label>
            <select class="form-control" id="role" name="role">
            % for key, value in company_roles.items():
              <option value="${key}">${value}</option>
            % endfor
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zamknij</button>
          <button type="submit" class="btn btn-primary" id="submit" name="submit">Zapisz</button>
        </div>
      </form>
    </div>
  </div>
</div>

<script>
  // Hide Project Modal
  var modalProjectEl = document.getElementById("add-project-modal");
  var modalProject = new bootstrap.Modal(modalProjectEl);
  document.getElementById("submit").addEventListener("click", function () {
    modalProject.hide();
  });
  // Clear input fields in Project Modal
  var btnAddProject = document.getElementById("btn-add-project");
  btnAddProject.addEventListener('click', function handleClick(event) {
    var projectName = document.getElementById("name");
    projectName.value = '';
    var stageElement = document.getElementById("stage");
    stageElement.selectedIndex = 0;
    var roleElement = document.getElementById("role");
    roleElement.selectedIndex = 0;
  });
</script> 