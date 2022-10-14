<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card border-0">
  <div class="row">
    <div class="col-9">
      <ul class="nav nav-pills">
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">Firma</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('company_projects', company_id=company.id, slug=company.slug)}">
            Projekty <span class="badge text-bg-secondary">${c_projects}</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="${request.route_url('company_tags', company_id=company.id, slug=company.slug)}">
            Tagi <span class="badge text-bg-secondary">${c_tags}</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link active" aria-current="page" href="${request.route_url('company_persons', company_id=company.id, slug=company.slug)}">
            Osoby <span class="badge text-bg-secondary"><div id="company-persons-counter" hx-get="${request.route_url('count_company_persons', company_id=company.id, slug=company.slug)}" hx-trigger="personCompanyEvent from:body">${c_persons}</div></span>
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
        <button id="btn-add-person" type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#add-person-modal">
          Dodaj
        </button>
        % else:
        <button type="button" class="btn btn-success" disabled>Dodaj</button>
        % endif
      </div>
    </div>
  </div>
</div>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>Imię i nazwisko</th>
        <th>Stanowisko</th>
        <th>Telefon</th>
        <th>Email</th>
        <th class="col-2">Akcja</th>
      </tr>
    </thead>
    <tbody id="new-person">
      % for person in company.people:
      <tr>
        <td><a href="${request.route_url('person_view', person_id=person.id, slug=person.slug)}">${person.name}</a></td>
        <td>${person.position}</td>
        <td>${person.phone}</td>
        <td><a href="mailto:${person.email}">${person.email}</a></td>
        <td class="col-2">
          <a class="btn btn-secondary btn-sm" href="${request.route_url('person_vcard', person_id=person.id, slug=person.slug)}">vCard</a>
          ${button.del_row('delete_person', person_id=person.id, slug=person.slug)}
        </td>
      </tr>
      % endfor
    </tbody>
  </table>
</div>

<div class="modal fade" id="add-person-modal" tabindex="-1" aria-labelledby="add-person-modal-label" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <form hx-post="${request.route_url('add_person', company_id=company.id, slug=company.slug)}" hx-target="#new-person" hx-swap="beforeend">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <div class="modal-header">
          <h5 class="modal-title" id="add-person-modal-label">Dodaj osobę</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="person-name" class="form-label">Imię i nazwisko</label>
            <input type="text" class="form-control" id="person-name" name="name" required minlength="5" maxlength="100">
          </div>
          <div class="mb-3">
            <label for="position" class="form-label">Stanowisko</label>
            <input type="text" class="form-control" id="position" name="position" maxlength="100">
          </div>
          <div class="mb-3">
            <label for="phone" class="form-label">Telefon</label>
            <input type="text" class="form-control" id="phone" name="phone" maxlength="50">
          </div>
          <div class="mb-3">
            <label for="email" class="form-label">Email</label>
            <input type="email" class="form-control" id="email" name="email" maxlength="50">
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zamknij</button>
          <button type="submit" class="btn btn-primary" id="btn-save-person">Zapisz</button>
        </div>
      </form>
    </div>
  </div>
</div>

<script>
  // Hide modal
  var modalPersonEl = document.getElementById("add-person-modal");
  var modalPerson = new bootstrap.Modal(modalPersonEl);
  var personName = document.getElementById("person-name");
  var personEmail = document.getElementById("email");
  document.getElementById("btn-save-person").addEventListener("click", function () {
    if (personName.checkValidity() && personEmail.checkValidity()) {
      modalPerson.hide();
    };
  });
  // Clear input fields
  var btnAddPerson = document.getElementById("btn-add-person");
  btnAddPerson.addEventListener('click', function handleClick(event) {
    var inputs = document.querySelectorAll("#person-name, #position, #phone, #email");
    inputs.forEach(input => {
      input.value = '';
    });
  });
</script>