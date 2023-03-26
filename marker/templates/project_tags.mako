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
        <a class="nav-link active" href="${request.route_url('project_tags', project_id=project.id, slug=project.slug)}">
          Tagi <span class="badge text-bg-secondary"><div hx-get="${request.route_url('project_count_tags', project_id=project.id, slug=project.slug)}" hx-trigger="tagEvent from:body">${project.count_tags}</div></span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('project_contacts', project_id=project.id, slug=project.slug)}">
          Kontakty <span class="badge text-bg-secondary">${project.count_contacts}</span>
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
          Podobne <span class="badge text-bg-secondary"><div id="similar-projects" hx-get="${request.route_url('project_count_similar', project_id=project.id, slug=project.slug)}" hx-trigger="tagEvent from:body">${project.count_similar}</div></span></a>
        </a>
      </li>
    </ul>
  </div>
  <div>
    % if request.identity.role == 'editor' or 'admin':
    <button id="btn-add-tag" type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#modal-add-tag">
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
        <th>Tag</th>
        <th class="col-2">Akcja</th>
      </tr>
    </thead>
    <tbody id="new-tag">
      % for tag in project.tags:
        <%include file="tag_row_project.mako" args="tag=tag, project=project"/>
      % endfor
    </tbody>
  </table>
</div>

<div class="modal fade" id="modal-add-tag" tabindex="-1" aria-labelledby="modal-add-tag-label" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <form hx-post="${request.route_url('project_add_tag', project_id=project.id, slug=project.slug)}" hx-target="#new-tag" hx-swap="beforeend">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <div class="modal-header">
          <h5 class="modal-title" id="modal-add-tag-label">Dodaj tag</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="name" class="form-label">Nazwa</label>
            <input list="tags" type="text" class="form-control" id="name" name="name" autocomplete="off" hx-get="${request.route_url('tag_select')}" hx-target="#tag-list" hx-swap="innerHTML" hx-trigger="keyup changed delay:250ms" required minlength="3" maxlength="50">
            <div id="tag-list"></div>
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
  var modalTagEl = document.getElementById("modal-add-tag");
  var modalTag = new bootstrap.Modal(modalTagEl);
  var tagName = document.getElementById("name");
  document.getElementById("submit").addEventListener("click", function () {
    if (tagName.checkValidity()) {
      modalTag.hide();
    };
  });
  // Clear input fields
  var btnAddTag = document.getElementById("btn-add-tag");
  btnAddTag.addEventListener('click', function handleClick(event) {
    var tagName = document.getElementById("name");
    tagName.value = '';
  });
</script>
