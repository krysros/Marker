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
          <h5 class="modal-title" id="modal-add-comment-label">${_("Add comment")}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="comment" class="form-label">${_("Comment")}</label>
            <textarea class="form-control" id="comment" name="comment"></textarea>
            <small class="text-body-secondary">${_("You can use Markdown for this field.")}</small>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">${_("Close")}</button>
          <button type="submit" class="btn btn-primary" id="submit" name="submit">${_("Save")}</button>
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