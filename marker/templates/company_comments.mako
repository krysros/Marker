<%inherit file="layout.mako"/>

<div class="card border-${company.color}">
  <div class="card-header">
    <div class="row">
      <div class="col-10">
        <ul class="nav nav-tabs card-header-tabs">
          <li class="nav-item">
            <a class="nav-link" href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">Firma</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="${request.route_url('company_projects', company_id=company.id, slug=company.slug)}">
              Projekty <span class="badge text-bg-secondary">${c_projects}</span>
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="${request.route_url('company_persons', company_id=company.id, slug=company.slug)}">
              Osoby <span class="badge text-bg-secondary">${c_persons}</span>
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="${request.route_url('company_tags', company_id=company.id, slug=company.slug)}">
              Tagi <span class="badge text-bg-secondary">${c_tags}</span>
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link active" aria-current="page" href="${request.route_url('company_comments', company_id=company.id, slug=company.slug)}">
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
      <div class="col-2">
        <div class="float-end">
          <button id="btn-add-comment" type="button" class="btn btn-success btn-sm" data-bs-toggle="modal" data-bs-target="#add-comment-modal">
            Dodaj
          </button>
        </div>
      </div>
    </div>
  </div>
  <div class="card-body">
    <p>Komentarze nt. firmy <strong>${company.name}</strong></p>
  </div>
</div>

<div id="last-comment"></div>
<%include file="comments_more.mako"/>

<div class="modal fade" id="add-comment-modal" tabindex="-1" aria-labelledby="add-comment-modal-label" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <form hx-post="${request.route_url('comment_add', company_id=company.id, slug=company.slug)}" hx-target="#last-comment" hx-swap="afterbegin">
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