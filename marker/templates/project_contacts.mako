<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">
    <ul class="nav nav-pills">
      <li class="nav-item">
        <a class="nav-link" aria-current="page" href="${request.route_url('project_view', project_id=project.id, slug=project.slug)}">Projekt</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('project_companies', project_id=project.id, slug=project.slug)}">
          Firmy <span class="badge text-bg-secondary">${project.count_companies}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('project_tags', project_id=project.id, slug=project.slug)}">
          Tagi <span class="badge text-bg-secondary">${project.count_tags}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link active" href="${request.route_url('project_contacts', project_id=project.id, slug=project.slug)}">
          Kontakty <span class="badge text-bg-secondary"><div hx-get="${request.route_url('project_count_contacts', project_id=project.id, slug=project.slug)}" hx-trigger="contactEvent from:body">${project.count_contacts}</div></span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('project_comments', project_id=project.id, slug=project.slug)}">
          Komentarze <span class="badge text-bg-secondary">${project.count_comments}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('project_watched', project_id=project.id, slug=project.slug)}">
          Obserwacje <span class="badge text-bg-secondary"><div hx-get="${request.route_url('project_count_watched', project_id=project.id, slug=project.slug)}" hx-trigger="watchEvent from:body">${project.count_watched}</div></span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('project_similar', project_id=project.id, slug=project.slug)}">
          Podobne <span class="badge text-bg-secondary">${project.count_similar}</span></a>
        </a>
      </li>
    </ul>
  </div>
  <div>
    % if request.identity.role == 'editor' or 'admin':
    <button id="btn-add-contact" type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#modal-add-contact">
      <i class="bi bi-plus-lg"></i>
    </button>
    % else:
    <button type="button" class="btn btn-success" disabled><i class="bi bi-plus-lg"></i></button>
    % endif
  </div>
</div>

<%include file="project_lead.mako"/>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th class="col-1">#</th>
        <th>Imię i nazwisko</th>
        <th>Rola</th>
        <th>Telefon</th>
        <th>Email</th>
        <th class="col-2">Akcja</th>
      </tr>
    </thead>
    <tbody id="new-contact">
      % for contact in project.contacts:
        <%include file="contact_row.mako" args="contact=contact"/>
      % endfor
    </tbody>
  </table>
</div>

<div class="modal fade" id="modal-add-contact" tabindex="-1" aria-labelledby="modal-add-contact-label" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <form hx-post="${request.route_url('project_add_contact', project_id=project.id, slug=project.slug)}" hx-target="#new-contact" hx-swap="beforeend">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <div class="modal-header">
          <h5 class="modal-title" id="modal-add-contact-label">Dodaj kontakt</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="name" class="form-label">Imię i nazwisko</label>
            <input type="text" class="form-control" id="name" name="name" required minlength="5" maxlength="100">
          </div>
          <div class="mb-3">
            <label for="role" class="form-label">Rola</label>
            <input type="text" class="form-control" id="role" name="role" maxlength="100">
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
          <button type="submit" class="btn btn-primary" id="submit" name="submit">Zapisz</button>
        </div>
      </form>
    </div>
  </div>
</div>

<script>
  // Hide modal
  var modalContactEl = document.getElementById("modal-add-contact");
  var modalContact = new bootstrap.Modal(modalContactEl);
  var contactName = document.getElementById("name");
  var contactEmail = document.getElementById("email");
  document.getElementById("submit").addEventListener("click", function () {
    if (contactName.checkValidity() && contactEmail.checkValidity()) {
      modalContact.hide();
    };
  });
  // Clear input fields
  var btnAddContact = document.getElementById("btn-add-contact");
  btnAddContact.addEventListener('click', function handleClick(event) {
    var inputs = document.querySelectorAll("#name, #role, #phone, #email");
    inputs.forEach(input => {
      input.value = '';
    });
  });
</script>