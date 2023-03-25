<%inherit file="layout.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">
    <ul class="nav nav-pills">
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">Firma</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_projects', company_id=company.id, slug=company.slug)}">
          Projekty <span class="badge text-bg-secondary">${company.count_projects}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_tags', company_id=company.id, slug=company.slug)}">
          Tagi <span class="badge text-bg-secondary">${company.count_tags}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_contacts', company_id=company.id, slug=company.slug)}">
          Kontakty <span class="badge text-bg-secondary">${company.count_contacts}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link active" aria-current="page" href="${request.route_url('company_comments', company_id=company.id, slug=company.slug)}">
          Komentarze <span class="badge text-bg-secondary"><div hx-get="${request.route_url('company_count_comments', company_id=company.id, slug=company.slug)}" hx-trigger="commentEvent from:body">${company.count_comments}</div></span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_recommended', company_id=company.id, slug=company.slug)}">
          Rekomendacje <span class="badge text-bg-secondary">${company.count_recommended}</span>
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_similar', company_id=company.id, slug=company.slug)}">
          Podobne <span class="badge text-bg-secondary">${company.count_similar}</span>
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

<%include file="company_lead.mako"/>

<div id="last-comment"></div>
<%include file="comment_more.mako"/>

<div class="modal fade" id="add-comment-modal" tabindex="-1" aria-labelledby="add-comment-modal-label" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <form hx-post="${request.route_url('add_comment_to_company', company_id=company.id, slug=company.slug)}" hx-target="#last-comment" hx-swap="afterbegin">
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
          <div class="mb-3">
            <p><small class="text-muted">W tym polu możesz skorzystać z Markdown.</small></p>
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