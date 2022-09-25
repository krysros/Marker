<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-body">
    <div class="float-end">
      <!-- Button trigger modal -->
      <button id="btn-add-company" type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#add-company-modal">
        Dodaj
      </button>
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
    </div>
  </div>
</div>

<p class="lead">Firmy, które brały udział w projekcie <a href="${request.route_url('project_view', project_id=project.id, slug=project.slug)}">${project.name}</a></p>
<div id="project-companies">
  <%include file="company_list.mako"/>
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