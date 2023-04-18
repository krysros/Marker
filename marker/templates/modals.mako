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
          </div>
          <div class="mb-3">
            <p><small class="text-muted">${_("You can use Markdown for this field.")}</small></p>
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
          <h5 class="modal-title" id="modal-add-tag-label">${_("Add tag")}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="name" class="form-label">${_("Name")}</label>
            <input list="tags" type="text" class="form-control" id="name" name="name" autocomplete="off" hx-get="${request.route_url('tag_select')}" hx-target="#tag-list" hx-swap="innerHTML" hx-trigger="keyup changed delay:250ms" required minlength="3" maxlength="50">
            <div id="tag-list"></div>
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
  // Hide modal
  var modalTagEl = document.getElementById("modal-add-tag");
  var modalTag = new bootstrap.Modal(modalTagEl);
  var tagName = document.getElementById("name");
  document.getElementById("submit").addEventListener("click", function () {
    if (tagName.checkValidity()) {
      modalTag.hide();
    };
  });
</script>
</%def>

<%def name="add_contact(obj)">
<div class="modal fade" id="modal-add-contact" tabindex="-1" aria-labelledby="modal-add-contact-label" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      % if isinstance(obj, Company):
      <form hx-post="${request.route_url('company_add_contact', company_id=obj.id, slug=obj.slug)}" hx-target="#new-contact" hx-swap="beforeend">
      % elif isinstance(obj, Project):
      <form hx-post="${request.route_url('project_add_contact', project_id=obj.id, slug=obj.slug)}" hx-target="#new-contact" hx-swap="beforeend">
      % endif
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <div class="modal-header">
          <h5 class="modal-title" id="modal-add-contact-label">${_("Add contact")}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="name" class="form-label">${_("Fullname")}</label>
            <input type="text" class="form-control" id="name" name="name" required minlength="5" maxlength="100">
          </div>
          <div class="mb-3">
            <label for="role" class="form-label">${_("Role")}</label>
            <input type="text" class="form-control" id="role" name="role" maxlength="100">
          </div>
          <div class="mb-3">
            <label for="phone" class="form-label">${_("Phone")}</label>
            <input type="text" class="form-control" id="phone" name="phone" maxlength="50">
          </div>
          <div class="mb-3">
            <label for="email" class="form-label">${_("Email")}</label>
            <input type="email" class="form-control" id="email" name="email" maxlength="50">
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
  // Hide modal
  var modalContactEl = document.getElementById("modal-add-contact");
  var modalContact = new bootstrap.Modal(modalContactEl);
  var contactName = document.getElementById("name");
  var contactEmail = document.getElementById("email");
  document.getElementById("submit").addEventListener("click", function () {
    if (contactName.checkValidity() && contactEmail.checkValidity()) {
      modalContact.hide();
    };
  });
</script>
</%def>

<%def name="add_company_project(obj)">
<div class="modal fade" id="modal-add-relation" tabindex="-1" aria-labelledby="modal-add-relation-label" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      % if isinstance(obj, Company):
      <form hx-post="${request.route_url('company_add_project', company_id=obj.id, slug=obj.slug)}" hx-target="#relation" hx-swap="innerHTML show:window:top">
      % elif isinstance(obj, Project):
      <form hx-post="${request.route_url('project_add_company', project_id=obj.id, slug=obj.slug)}" hx-target="#relation" hx-swap="innerHTML show:window:top">
      % endif
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <div class="modal-header">
          <h5 class="modal-title" id="add-relation-label">Dodaj relację</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="name" class="form-label">${_("Name")}</label>
            % if isinstance(obj, Company):
            <input list="projects" type="text" class="form-control" id="name" name="name" autocomplete="off" hx-get="${request.route_url('project_select')}" hx-target="#select-list" hx-swap="innerHTML" hx-trigger="keyup changed delay:250ms" required maxlength="200">
            % elif isinstance(obj, Project):
            <input list="companies" type="text" class="form-control" id="name" name="name" autocomplete="off" hx-get="${request.route_url('company_select')}" hx-target="#select-list"  hx-swap="innerHTML" hx-trigger="keyup changed delay:250ms" required maxlength="100">
            % endif
            <div id="select-list"></div>
          </div>
          <div class="mb-3">
            <label for="stage">${_("Stage")}</label>
            <select class="form-control" id="stage" name="stage">
            % for key, value in stages.items():
              <option value="${key}">${value}</option>
            % endfor
            </select>
          </div>
          <div class="mb-3">
            <label for="role">${_("Role")}</label>
            <select class="form-control" id="role" name="role">
            % for key, value in company_roles.items():
              <option value="${key}">${value}</option>
            % endfor
            </select>
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
  // Hide Relation Modal
  var modalRelationEl = document.getElementById("modal-add-relation");
  var modalRelation = new bootstrap.Modal(modalRelationEl);
  document.getElementById("submit").addEventListener("click", function () {
    modalRelation.hide();
  });
</script>
</%def>