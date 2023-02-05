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
        <a class="nav-link" href="${request.route_url('project_contacts', project_id=project.id, slug=project.slug)}">
          Kontakty <span class="badge text-bg-secondary">${project.count_contacts}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link active" href="${request.route_url('project_comments', project_id=project.id, slug=project.slug)}">
        Komentarze <span class="badge text-bg-secondary"><div id="project-comments-counter" hx-get="${request.route_url('count_project_comments', project_id=project.id, slug=project.slug)}" hx-trigger="commentProjectEvent from:body">${project.count_comments}</div></span>
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
    <button id="btn-add-comment" type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#add-comment-modal">
      <i class="bi bi-plus-lg"></i>
    </button>
    % else:
    <button type="button" class="btn btn-success" disabled><i class="bi bi-plus-lg"></i></button>
    % endif
  </div>
</div>

<%include file="project_lead.mako"/>

<div id="last-comment"></div>
<%include file="comment_more.mako"/>

<div class="modal fade" id="add-comment-modal" tabindex="-1" aria-labelledby="add-comment-modal-label" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <form hx-post="${request.route_url('comment_project', project_id=project.id, slug=project.slug)}" hx-target="#last-comment" hx-swap="afterbegin">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <div class="modal-header">
          <h5 class="modal-title" id="add-comment-modal-label">Dodaj komentarz</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="comment" class="form-label">Komentarz</label>
            <textarea class="form-control" id="comment" name="comment"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Zamknij</button>
          <button type="submit" class="btn btn-primary" id="btn-save-comment">Zapisz</button>
        </div>
      </form>
    </div>
  </div>
</div>

<script>
  // Hide Comment Modal
  var modalCommentEl = document.getElementById("add-comment-modal");
  var modalComment = new bootstrap.Modal(modalCommentEl);
  document.getElementById("btn-save-comment").addEventListener("click", function () {
    modalComment.hide();
  });
  // Clear input fields in Comment Modal
  var btnAddComment = document.getElementById("btn-add-comment");
  btnAddComment.addEventListener('click', function handleClick(event) {
    var comment = document.getElementById("comment");
    comment.value = '';
  });
</script>