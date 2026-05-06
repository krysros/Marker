<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-tags"></i> ${_("Selected tags")}
    <span class="badge bg-secondary">${counter}</span>
  </h2>
  <div class="d-flex flex-wrap gap-2 justify-content-md-end w-100 w-md-auto">
    ${button.deselect_selected(url=request.route_url('user_deselect_tags', username=user.name), confirm_text=_("Deselect all selected tags?"))}
    ${button.delete_selected(url=request.route_url('user_delete_selected_tags', username=user.name))}
    <button type="button" class="btn btn-info" data-bs-toggle="modal" data-bs-target="#mergeTagsModal">
      <i class="bi bi-diagram-2"></i>
    </button>
    <% from marker.utils.export_columns import tag_company_cols, tag_project_cols; _export_cols = tag_project_cols(_) if q.get('category') == 'projects' else tag_company_cols(_) %>
    ${button.dropdown_download_cols(request.route_url('user_export_selected_tags', username=user.name, _query=q), _export_cols)}
  </div>
</div>
<hr>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div class="dropdown">
    <button type="button" class="btn btn-sm btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
      <i class="bi bi-filter"></i> ${_("Filter")}
    </button>
    <form class="dropdown-menu p-4" style="min-width: 200px;">
      <input type="hidden" name="sort" value="${q.get('sort', 'created_at')}">
      <input type="hidden" name="order" value="${q.get('order', 'desc')}">
      <div class="mb-3">
        <label class="form-label" for="category">${_("Category")}</label>
        <select class="form-control" id="category" name="category">
          % for k, v in categories.items():
            <option value="${k}" ${'selected' if q.get('category', '') == k else ''}>${v}</option>
          % endfor
        </select>
      </div>
      <button type="submit" class="btn btn-primary">${_("Submit")}</button>
    </form>
  </div>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
  <div class="btn-group btn-group-sm ms-auto" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-primary" href="${request.route_url('user_selected_tags', username=user.name, _query=q)}"><i class="bi bi-tags"></i> ${_("Tags")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_companies', username=user.name)}"><i class="bi bi-buildings"></i> ${_("Companies")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_projects', username=user.name)}"><i class="bi bi-briefcase"></i> ${_("Projects")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts', username=user.name)}"><i class="bi bi-people"></i> ${_("Contacts")}</a>
  </div>
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
            <small class="form-text text-body-secondary">${_("The new name can be the same as one of the selected tags")}</small>
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