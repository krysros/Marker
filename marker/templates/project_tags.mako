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
          Tagi <span class="badge text-bg-secondary"><div hx-get="${request.route_url('count_project_tags', project_id=project.id, slug=project.slug)}" hx-trigger="tagEvent from:body">${project.count_tags}</div></span>
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
          Obserwacje <span class="badge text-bg-secondary"><div hx-get="${request.route_url('count_project_watched', project_id=project.id, slug=project.slug)}" hx-trigger="watchedProjectEvent from:body">${project.count_watched}</div></span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('project_similar', project_id=project.id, slug=project.slug)}">
          Podobne <span class="badge text-bg-secondary"><div id="similar-projects" hx-get="${request.route_url('count_project_similar', project_id=project.id, slug=project.slug)}" hx-trigger="tagEvent from:body">${project.count_similar}</div></span></a>
        </a>
      </li>
    </ul>
  </div>
  <div>
    % if request.identity.role == 'editor' or 'admin':
    <button id="btn-add-tag" type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#add-tag-modal">
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
      <tr>
        <td>${checkbox.tag(tag)}</td>
        <td><a href="${request.route_url('tag_view', tag_id=tag.id, slug=tag.slug)}">${tag.name}</a></td>
        <td class="col-2">${button.unlink('unlink_tag_from_project', project_id=project.id, tag_id=tag.id, size='sm')}</td>
      </tr>
      % endfor
    </tbody>
  </table>
</div>

<div class="modal fade" id="add-tag-modal" tabindex="-1" aria-labelledby="add-tag-modal-label" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <form hx-post="${request.route_url('add_tag_to_project', project_id=project.id, slug=project.slug)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-target="#new-tag" hx-swap="beforeend">
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
