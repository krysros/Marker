<%include file="navbar.mako"/>

<div class="card">
  <div class="card-body">
    <div class="float-end">
      <!-- Button trigger modal -->
      <button id="btn-add-comment" type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#add-comment-modal">
        Dodaj
      </button>
      <!-- Modal -->
      <div class="modal fade" id="add-comment-modal" tabindex="-1" aria-labelledby="add-comment-modal-label" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <form hx-post="${request.route_url('comment_add', company_id=company.id, slug=company.slug)}" hx-target="#last-comment" hx-swap="afterbegin">
              <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
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
    </div>
  </div>
</div>

<p class="lead">Komentarze nt. firmy <a href="#top" hx-get="${request.route_url('company_view', company_id=company.id, slug=company.slug)}" hx-target="#main-container">${company.name}</a></p>

<div id="last-comment"></div>
<%include file="comment_more.mako"/>

<script>
  // Hide Comment Modal
  const modalCommentEl = document.getElementById("add-comment-modal");
  const modalComment = new bootstrap.Modal(modalCommentEl);
  document.getElementById("btn-save-comment").addEventListener("click", function () {
    modalComment.hide();
  });
  // Clear input fields in Comment Modal
  const btnAddComment = document.getElementById("btn-add-comment");
  btnAddComment.addEventListener('click', function handleClick(event) {
    const comment = document.getElementById("comment");
    comment.value = '';
  });
</script>