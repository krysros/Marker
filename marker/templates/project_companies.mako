<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-header">
    <div class="row">
      <div class="col-10">
        <ul class="nav nav-tabs card-header-tabs">
          <li class="nav-item">
            <a class="nav-link" href="${request.route_url('project_view', project_id=project.id, slug=project.slug)}">Projekt</a>
          </li>
        ##      <li class="nav-item">
        ##        <a class="nav-link" href="${request.route_url('project_comments', project_id=project.id, slug=project.slug)}">
        ##        Komentarze <span class="badge text-bg-secondary">${c_comments}</span>
        ##        </a>
        ##      </li>
          <li class="nav-item">
            <a class="nav-link" href="${request.route_url('project_watched', project_id=project.id, slug=project.slug)}">
              Obserwacje <span class="badge text-bg-secondary">${c_watched}</span></a>
          </li>
          <li class="nav-item">
            <a class="nav-link active" aria-current="page" href="${request.route_url('project_companies', project_id=project.id, slug=project.slug)}">
              Firmy <span class="badge text-bg-secondary">${c_companies}</span>
            </a>
          </li>
        ##      <li class="nav-item">
        ##        <a class="nav-link" href="${request.route_url('project_similar', project_id=project.id, slug=project.slug)}">
        ##          Podobne <span class="badge text-bg-secondary">${c_simiar}</span></a>
        ##        </a>
        ##      </li>
        </ul>
      </div>
      <div class="col-2">
        <div class="float-end">
          % if request.identity.role == 'editor':
          <!-- Button trigger modal -->
          <button id="btn-add-company" type="button" class="btn btn-success btn-sm" data-bs-toggle="modal" data-bs-target="#add-company-modal">
            Dodaj
          </button>
          % else:
          <button type="button" class="btn btn-success btn-sm" disabled>Dodaj</button>
          % endif
        </div>
      </div>
    </div>
  </div>
  <div class="card-body">
    <p>Firmy, które brały udział w projekcie <a href="${request.route_url('project_view', project_id=project.id, slug=project.slug)}">${project.name}</a></p>
  </div>
</div>

<div id="project-companies">
  <%include file="company_list.mako"/>
</div>

<!-- Modal -->
<div class="modal fade" id="add-company-modal" tabindex="-1" aria-labelledby="add-company-modal-label" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <form hx-post="${request.route_url('add_company', project_id=project.id, slug=project.slug)}" hx-target="#project-companies" hx-swap="innerHTML show:window:top">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <div class="modal-header">
          <h5 class="modal-title" id="add-company-modal-label">Dodaj firmę</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="company-name" class="form-label">Nazwa</label>
            <input list="companies" type="text" class="form-control" id="company-name" name="name" autocomplete="off" hx-get="${request.route_url('company_select')}" hx-target="#company-list"  hx-swap="innerHTML" hx-trigger="keyup changed delay:250ms" required maxlength="100">
            <div id="company-list"></div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zamknij</button>
          <button type="submit" class="btn btn-primary" id="btn-save-company">Zapisz</button>
        </div>
      </form>
    </div>
  </div>
</div>

<script>
  // Hide Company Modal
  var modalCompanyEl = document.getElementById("add-company-modal");
  var modalCompany = new bootstrap.Modal(modalCompanyEl);
  document.getElementById("btn-save-company").addEventListener("click", function () {
    modalCompany.hide();
  });
  // Clear input fields in Company Modal
  var btnAddCompany = document.getElementById("btn-add-company");
  btnAddCompany.addEventListener('click', function handleClick(event) {
    var companyName = document.getElementById("company-name");
    companyName.value = '';
  });
</script>