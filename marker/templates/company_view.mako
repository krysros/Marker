<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="card">
  <div class="card-body">
    <div class="float-end">
      <button hx-post="${request.route_url('company_recommend', company_id=company.id)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-target="#recomended" class="btn btn-primary">
        <div id="recomended">
          % if company in request.identity.recomended:
            <i class="bi bi-hand-thumbs-up-fill"></i>
          % else:
            <i class="bi bi-hand-thumbs-up"></i>
          % endif
        </div>
      </button>
      ${button.edit('company_edit', company_id=company.id, slug=company.slug)}
      ${button.danger('company_delete', 'Usuń', company_id=company.id, slug=company.slug)}
    </div>
  </div>
</div>

<div class="card border-${company.color}">
  <div class="card-header">
    <i class="bi bi-building"></i> Firma
    <div class="float-end">
      <div class="form-check">
        % if company in request.identity.checked:
        <input class="form-check-input"
              id="mark"
              type="checkbox"
              value="${company.id}"
              autocomplete="off"
              checked
              hx-post="${request.route_url('company_check', company_id=company.id)}"
              hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
              hx-trigger="click"
              hx-swap="none">
        % else:
        <input class="form-check-input"
              id="mark"
              type="checkbox"
              value="${company.id}"
              autocomplete="off"
              hx-post="${request.route_url('company_check', company_id=company.id)}"
              hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
              hx-trigger="click"
              hx-swap="none">
        % endif
        <label class="form-check-label" for="mark">Zaznacz</label>
      </div>
    </div>
  </div>
  <div class="card-body">
    <div class="row">
      <div class="col">
        <h1>${company.name}</h1>
      </div>
    </div>
    <div class="row">
      <div class="col">
        <dl class="dl-horizontal">
          <dt>Adres</dt>
          <dd>
            ${company.street}<br>
            % if company.postcode:
            ${company.postcode} ${company.city}<br>
            % else:
            ${company.city}<br>
            % endif
            ${states.get(company.state)}<br>
          </dd>
          <dt>Link</dt>
          <dd>
          % if company.WWW.startswith('http'):
            <a href="${company.WWW}">
          % else:
            <a href="${'http://' + company.WWW}">
          % endif
            ${company.WWW}</a>
          </dd>
        </dl>    
      </div>
      <div class="col">
        <dl>
          <dt>Dane rejestrowe</dt>
          <dd>
            NIP: ${company.NIP or "brak"}<br>
            REGON: ${company.REGON or "brak"}<br>
            KRS: ${company.KRS or "brak"}
            % if company.court:
              <br>${courts.get(company.court)}
            % endif
          </dd>
        </dl>
      </div>
    </div>
  </div>
  <div class="card-footer">
    <ul class="nav">
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_comments', company_id=company.id, slug=company.slug)}">
          % if c_comments > 0:
          Komentarze <span class="badge text-bg-warning">${c_comments}</span>
          % else:
          Komentarze <span class="badge text-bg-secondary">0</span>
          % endif
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_recomended', company_id=company.id, slug=company.slug)}">
          % if c_recomended > 0:
          Rekomendacje <span class="badge text-bg-success">${c_recomended}</span>
          % else:
          Rekomendacje <span class="badge text-bg-secondary">0</span>
          % endif
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_projects', company_id=company.id, slug=company.slug)}">
          % if c_projects > 0:
          Projekty <span class="badge text-bg-info">${c_projects}</span>
          % else:
          Projekty <span class="badge text-bg-secondary">0</span>
          % endif
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_similar', company_id=company.id, slug=company.slug)}">
        % if c_similar > 0:
        Podobne <span class="badge text-bg-dark">${c_similar}</span>
        % else:
        Podobne <span class="badge text-bg-secondary">0</span>
        % endif
        </a>
      </li>
    </ul>
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="bi bi-people"></i> Osoby</div>
  <div class="card-body">
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
            <td><a href="${request.route_url('person_view', person_id=person.id)}">${person.name}</a></td>
            <td>${person.position}</td>
            <td>${person.phone}</td>
            <td><a href="mailto:${person.email}">${person.email}</a></td>
            <td class="col-2">
              <a class="btn btn-secondary btn-sm" href="${request.route_url('person_vcard', person_id=person.id)}">vCard</a>
              ${button.del_row('person_delete_from_company', person_id=person.id)}
            </td>
          </tr>
          % endfor
        </tbody>
      </table>
    </div>
    % if request.identity.role == 'editor':
    <!-- Button trigger modal -->
    <button id="btn-add-person" type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#add-person-modal">
      Dodaj
    </button>
    % else:
    <button type="button" class="btn btn-success" disabled>Dodaj</button>
    % endif
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="bi bi-tags"></i> Tagi</div>
  <div class="card-body">
    <div class="table-responsive">
      <table class="table table-striped">
        <thead>
          <tr>
            <th>Tag</th>
            <th class="col-2">Akcja</th>
          </tr>
        </thead>
        <tbody id="new-tag">
          % for tag in company.tags:
          <tr>
            <td><a href="${request.route_url('tag_view', tag_id=tag.id, slug=tag.slug)}">${tag.name}</a></td>
            <td class="col-2">${button.del_row('delete_tag', company_id=company.id, tag_id=tag.id)}</td>
          </tr>
          % endfor
        </tbody>
      </table>
    </div>
    % if request.identity.role == 'editor':
    <!-- Button trigger modal -->
    <button id="btn-add-tag" type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#add-tag-modal">
      Dodaj
    </button>
    % else:
    <button type="button" class="btn btn-success" disabled>Dodaj</button>
    % endif
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="bi bi-clock"></i> Data modyfikacji</div>
  <div class="card-body">
    <p>
      Utworzono: ${company.created_at.strftime('%Y-%m-%d %H:%M:%S')}
      % if company.created_by:
        przez <a href="${request.route_url('user_view', username=company.created_by.name, what='info')}">${company.created_by.name}</a>
      % endif
      <br>
      % if company.updated_at:
        Zmodyfikowano: ${company.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if company.updated_by:
          przez <a href="${request.route_url('user_view', username=company.updated_by.name, what='info')}">${company.updated_by.name}</a>
        % endif
      % endif
    </p>
  </div>
</div>

<!-- Tag Modal -->
<div class="modal fade" id="add-tag-modal" tabindex="-1" aria-labelledby="add-tag-modal-label" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <form hx-post="${request.route_url('add_tag', company_id=company.id, slug=company.slug)}" hx-target="#new-tag" hx-swap="beforeend">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <div class="modal-header">
          <h5 class="modal-title" id="add-tag-modal-label">Dodaj tag</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="tag-name" class="form-label">Nazwa</label>
            <input list="tags" type="text" class="form-control" id="tag-name" name="name" autocomplete="off" hx-get="${request.route_url('tag_select')}" hx-target="#tag-list" hx-swap="innerHTML" hx-trigger="keyup changed delay:250ms" required minlength="3" maxlength="50">
            <div id="tag-list"></div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zamknij</button>
          <button type="submit" class="btn btn-primary" id="btn-save-tag">Zapisz</button>
        </div>
      </form>
    </div>
  </div>
</div>

<!-- Person Modal -->
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
            <label for="person-name" class="form-label">Nazwa</label>
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
  // Hide Tag Modal
  var modalTagEl = document.getElementById("add-tag-modal");
  var modalTag = new bootstrap.Modal(modalTagEl);
  var tagName = document.getElementById("tag-name");
  document.getElementById("btn-save-tag").addEventListener("click", function () {
    if (tagName.checkValidity()) {
      modalTag.hide();
    };
  });
  // Clear input fields in Tag Modal
  var btnAddTag = document.getElementById("btn-add-tag");
  btnAddTag.addEventListener('click', function handleClick(event) {
    var tagName = document.getElementById("tag-name");
    tagName.value = '';
  });

  // Hide Person Modal
  var modalPersonEl = document.getElementById("add-person-modal");
  var modalPerson = new bootstrap.Modal(modalPersonEl);
  var personName = document.getElementById("person-name");
  var personEmail = document.getElementById("email");
  document.getElementById("btn-save-person").addEventListener("click", function () {
    if (personName.checkValidity() && personEmail.checkValidity()) {
      modalPerson.hide();
    };
  });
  // Clear input fields in Person Modal
  var btnAddPerson = document.getElementById("btn-add-person");
  btnAddPerson.addEventListener('click', function handleClick(event) {
    var inputs = document.querySelectorAll("#person-name, #position, #phone, #email");
    inputs.forEach(input => {
      input.value = '';
    });
  });
</script>