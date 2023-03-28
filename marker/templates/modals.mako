<%!
  from marker.models import Company, Project
%>

<%def name="add_comment(obj)">
<div class="modal fade" id="modal-add-comment" tabindex="-1" aria-labelledby="modal-add-comment-label" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      % if isinstance(obj, Company):
      <form hx-post="${request.route_url('company_add_comment', company_id=obj.id, slug=obj.slug)}" hx-target="#last-comment" hx-swap="afterbegin">
      % elif isinstance(obj, Project):
      <form hx-post="${request.route_url('project_add_comment', project_id=obj.id, slug=obj.slug)}" hx-target="#last-comment" hx-swap="afterbegin">
      % endif
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <div class="modal-header">
          <h5 class="modal-title" id="modal-add-comment-label">Dodaj komentarz</h5>
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
          <button type="submit" class="btn btn-primary" id="submit" name="submit">Zapisz</button>
        </div>
      </form>
    </div>
  </div>
</div>
 
<script>
  // Hide Comment Modal
  var modalCommentEl = document.getElementById("modal-add-comment");
  var modalComment = new bootstrap.Modal(modalCommentEl);
  document.getElementById("submit").addEventListener("click", function () {
    modalComment.hide();
  });
  // Clear input fields in Comment Modal
  var btnAddComment = document.getElementById("btn-add-comment");
  btnAddComment.addEventListener('click', function handleClick(event) {
    var comment = document.getElementById("comment");
    comment.value = '';
  });
</script>
</%def>


<%def name="add_tag(obj)">
<div class="modal fade" id="modal-add-tag" tabindex="-1" aria-labelledby="modal-add-tag-label" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      % if isinstance(obj, Company):
      <form hx-post="${request.route_url('company_add_tag', company_id=obj.id, slug=obj.slug)}" hx-target="#new-tag" hx-swap="beforeend">
      % elif isinstance(obj, Project):
      <form hx-post="${request.route_url('project_add_tag', project_id=obj.id, slug=obj.slug)}" hx-target="#new-tag" hx-swap="beforeend">
      % endif
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
</%def>