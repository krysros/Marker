<%include file="navbar.mako"/>
<%namespace name="modal" file="modal.mako"/>

<div class="card">
  <div class="card-body">
    <div class="float-end">
      <button hx-post="${request.route_url('company_recommend', company_id=company.id)}" hx-target="#recomended" class="btn btn-primary">
        <div id="recomended">
          % if company in request.identity.recomended:
            <i class="bi bi-hand-thumbs-up-fill"></i>
          % else:
            <i class="bi bi-hand-thumbs-up"></i>
          % endif
        </div>
      </button>
      <a class="btn btn-warning" role="button" href="#" hx-get="${request.route_url('company_edit', company_id=company.id, slug=company.slug)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Edytuj</a>
      ${modal.danger_dialog('company_delete', 'Usuń', 'Czy na pewno chcesz usunąć firmę z bazy danych?', company_id=company.id, slug=company.slug)}
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
              hx-trigger="click"
              hx-swap="none">
        % else:
        <input class="form-check-input"
              id="mark"
              type="checkbox"
              value="${company.id}"
              autocomplete="off"
              hx-post="${request.route_url('company_check', company_id=company.id)}"
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
        % if c_comments:
        <a class="nav-link text-warning" role="button" href="#" hx-get="${request.route_url('company_comments', company_id=company.id, slug=company.slug)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Komentarze (${c_comments})</a>
        % else:
        <a class="nav-link" role="button" href="#" hx-get="${request.route_url('company_comments', company_id=company.id, slug=company.slug)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Komentarze (${c_comments})</a>
        % endif
      </li>
      <li class="nav-item">
        % if c_recomended:
        <a class="nav-link text-success" role="button" href="#" hx-get="${request.route_url('company_recomended', company_id=company.id, slug=company.slug)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Rekomendacje (${c_recomended})</a>
        % else:
        <a class="nav-link" role="button" href="#" hx-get="${request.route_url('company_recomended', company_id=company.id, slug=company.slug)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Rekomendacje (${c_recomended})</a>
        % endif
      </li>
      <li class="nav-item">
        <a class="nav-link" role="button" href="#" hx-get="${request.route_url('company_projects', company_id=company.id, slug=company.slug)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Projekty (${c_projects})</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" role="button" href="#" hx-get="${request.route_url('company_similar', company_id=company.id, slug=company.slug)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Podobne (${c_similar})</a>
      </li>
    </ul>
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="bi bi-people"></i> Osoby</div>
  <div class="card-body">
    <div id="company-people">
      <%include file="company_people.mako"/>
    </div>
    <!-- Button trigger modal -->
    <button id="btn-add-person" type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#add-person-modal">
      Dodaj
    </button>
    <!-- Modal -->
    <div class="modal fade" id="add-person-modal" tabindex="-1" aria-labelledby="add-person-modal-label" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <form hx-post="${request.route_url('company_people', company_id=company.id, slug=company.slug)}" hx-target="#company-people" hx-swap="innerHTML show:window:top">
            <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
            <div class="modal-header">
              <h5 class="modal-title" id="add-person-modal-label">Dodaj osobę</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <div class="mb-3">
                <label for="person-name" class="form-label">Nazwa</label>
                <input type="text" class="form-control" id="person-name" name="name" required>
              </div>
              <div class="mb-3">
                <label for="position" class="form-label">Stanowisko</label>
                <input type="text" class="form-control" id="position" name="position">
              </div>
              <div class="mb-3">
                <label for="phone" class="form-label">Telefon</label>
                <input type="text" class="form-control" id="phone" name="phone">
              </div>
              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" class="form-control" id="email" name="email">
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
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="bi bi-tags"></i> Tagi</div>
  <div class="card-body">
    <div id="company-tags">
      <%include file="company_tags.mako"/>
    </div>
    <!-- Button trigger modal -->
    <button id="btn-add-tag" type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#add-tag-modal">
      Dodaj
    </button>
    <!-- Modal -->
    <div class="modal fade" id="add-tag-modal" tabindex="-1" aria-labelledby="add-tag-modal-label" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <form hx-post="${request.route_url('company_tags', company_id=company.id, slug=company.slug)}" hx-target="#company-tags" hx-swap="innerHTML show:window:top">
            <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
            <div class="modal-header">
              <h5 class="modal-title" id="add-tag-modal-label">Dodaj tag</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <div class="mb-3">
                <label for="tag-name" class="form-label">Nazwa</label>
                <input list="tags" type="text" class="form-control" id="tag-name" name="name" autocomplete="off" hx-get="${request.route_url('tag_select')}" hx-target="#tag-list" hx-trigger="keyup changed delay:250ms" required>
                <div id="tag-list">
                  <%include file="tag_datalist.mako"/>
                </div>
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
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="bi bi-clock"></i> Data modyfikacji</div>
  <div class="card-body">
    <p>
      Utworzono: ${company.created_at.strftime('%Y-%m-%d %H:%M:%S')}
      % if company.created_by:
        przez <a href="#" hx-get="${request.route_url('user_view', username=company.created_by.name, what='info')}" hx-target="#main-container" hx-swap="innerHTML show:window:top">${company.created_by.name}</a>
      % endif
      <br>
      % if company.updated_at:
        Zmodyfikowano: ${company.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if company.updated_by:
          przez <a href="#" hx-get="${request.route_url('user_view', username=company.updated_by.name, what='info')}" hx-target="#main-container" hx-swap="innerHTML show:window:top">${company.updated_by.name}</a>
        % endif
      % endif
    </p>
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