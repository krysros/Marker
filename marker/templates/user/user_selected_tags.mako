<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-check-square"></i> ${_("Tags")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.delete_selected(url=request.route_url('user_delete_selected_tags', username=user.name))}
    ${button.button(icon='square', color='warning', url=request.route_url('user_clear_selected_tags', username=user.name))}
    <button type="button" class="btn btn-info" data-bs-toggle="modal" data-bs-target="#mergeTagsModal">
      <i class="bi bi-diagram-2"></i>
    </button>
    ${button.a(icon='download', color='primary', url=request.route_url('user_export_selected_tags', username=user.name, _query=q))}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div class="me-auto">${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="tag_table.mako"/>

<!-- Merge Tags Modal -->
<div class="modal fade" id="mergeTagsModal" tabindex="-1" aria-labelledby="mergeTagsModalLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h1 class="modal-title fs-5" id="mergeTagsModalLabel">
          <i class="bi bi-diagram-2"></i> ${_("Merge selected tags")}
        </h1>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <form hx-post="${request.route_url('user_merge_selected_tags', username=user.name)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'>
        <div class="modal-body">
          <div class="mb-3">
            <label for="mergeTagName" class="form-label">${_("New tag name")}</label>
            <input type="text" class="form-control" id="mergeTagName" name="merge_tag_name" required>
            <small class="form-text text-muted">${_("The new name can be the same as one of the selected tags")}</small>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">${_("Cancel")}</button>
          <button type="submit" class="btn btn-primary">${_("Merge")}</button>
        </div>
      </form>
    </div>
  </div>
</div>