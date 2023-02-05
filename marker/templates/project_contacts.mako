<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

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
          Kontakty <span class="badge text-bg-secondary"><div id="project-contacts-counter" hx-get="${request.route_url('count_project_contacts', project_id=project.id, slug=project.slug)}" hx-trigger="contactProjectEvent from:body">${project.count_contacts}</div></span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('project_comments', project_id=project.id, slug=project.slug)}">
        Komentarze <span class="badge text-bg-secondary">${project.count_comments}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('project_watched', project_id=project.id, slug=project.slug)}">
          Obserwacje <span class="badge text-bg-secondary"><div id="project-watched-counter" hx-get="${request.route_url('count_project_watched', project_id=project.id, slug=project.slug)}" hx-trigger="watchedProjectEvent from:body">${project.count_watched}</div></span></a>
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
    <button id="btn-add-contact" type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#add-contact-modal">
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
        <th>Imię i nazwisko</th>
        <th>Rola</th>
        <th>Telefon</th>
        <th>Email</th>
        <th class="col-2">Akcja</th>
      </tr>
    </thead>
    <tbody id="new-contact">
      % for contact in project.contacts:
      <tr>
        <td><a href="${request.route_url('contact_view', contact_id=contact.id, slug=contact.slug)}">${contact.name}</a></td>
        <td>${contact.role}</td>
        <td>${contact.phone}</td>
        <td><a href="mailto:${contact.email}">${contact.email}</a></td>
        <td class="col-2">
          ${button.vcard('contact_vcard', contact_id=contact.id, slug=contact.slug, size='sm')}
          ${button.del_row('delete_contact', contact_id=contact.id, slug=contact.slug, size='sm')}
        </td>
      </tr>
      % endfor
    </tbody>
  </table>
</div>

<div class="modal fade" id="add-contact-modal" tabindex="-1" aria-labelledby="add-contact-modal-label" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <form hx-post="${request.route_url('add_contact_to_project', project_id=project.id, slug=project.slug)}" hx-target="#new-contact" hx-swap="beforeend">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <div class="modal-header">
          <h5 class="modal-title" id="add-contact-modal-label">Dodaj kontakt</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="contact-name" class="form-label">Imię i nazwisko</label>
            <input type="text" class="form-control" id="contact-name" name="name" required minlength="5" maxlength="100">
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
          <button type="submit" class="btn btn-primary" id="btn-save-contact">Zapisz</button>
        </div>
      </form>
    </div>
  </div>
</div>

<script>
  // Hide modal
  var modalContactEl = document.getElementById("add-contact-modal");
  var modalContact = new bootstrap.Modal(modalContactEl);
  var contactName = document.getElementById("contact-name");
  var contactEmail = document.getElementById("email");
  document.getElementById("btn-save-contact").addEventListener("click", function () {
    if (contactName.checkValidity() && contactEmail.checkValidity()) {
      modalContact.hide();
    };
  });
  // Clear input fields
  var btnAddContact = document.getElementById("btn-add-contact");
  btnAddContact.addEventListener('click', function handleClick(event) {
    var inputs = document.querySelectorAll("#contact-name, #role, #phone, #email");
    inputs.forEach(input => {
      input.value = '';
    });
  });
</script>