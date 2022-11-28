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
          <a class="nav-link active" aria-current="page" href="${request.route_url('company_tags', company_id=company.id, slug=company.slug)}">
            Tagi <span class="badge text-bg-secondary"><div id="company-tags-counter" hx-get="${request.route_url('count_company_tags', company_id=company.id, slug=company.slug)}" hx-trigger="tagCompanyEvent from:body">${c_tags}</div></span>
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
          <a class="nav-link" href="${request.route_url('company_recommended', company_id=company.id, slug=company.slug)}">
            Rekomendacje <span class="badge text-bg-secondary">${c_recommended}</span>
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
        <button id="btn-add-tag" type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#add-tag-modal">
          <i class="bi bi-plus-lg"></i>
        </button>
        % else:
        <button type="button" class="btn btn-success" disabled><i class="bi bi-plus-lg"></i></button>
        % endif
      </div>
    </div>
  </div>
</div>

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
        <td class="col-2">${button.unlink('unlink_tag', company_id=company.id, tag_id=tag.id)}</td>
      </tr>
      % endfor
    </tbody>
  </table>
</div>

<div class="modal fade" id="add-tag-modal" tabindex="-1" aria-labelledby="add-tag-modal-label" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <form hx-post="${request.route_url('add_tag', company_id=company.id, slug=company.slug)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-target="#new-tag" hx-swap="beforeend">
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

<script>
  // Hide modal
  var modalTagEl = document.getElementById("add-tag-modal");
  var modalTag = new bootstrap.Modal(modalTagEl);
  var tagName = document.getElementById("tag-name");
  document.getElementById("btn-save-tag").addEventListener("click", function () {
    if (tagName.checkValidity()) {
      modalTag.hide();
    };
  });
  // Clear input fields
  var btnAddTag = document.getElementById("btn-add-tag");
  btnAddTag.addEventListener('click', function handleClick(event) {
    var tagName = document.getElementById("tag-name");
    tagName.value = '';
  });
</script>