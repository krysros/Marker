<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<%! from marker.utils.export_columns import tag_company_cols, tag_project_cols %>
<% _export_cols = tag_project_cols(_) if q.get('category') == 'projects' else tag_company_cols(_) %>
<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <div class="me-auto">${pills.pills(user_pills, active_url=request.route_url('user_tags', username=user.name))}</div>
  <div>${button.dropdown_download_cols(request.route_url('user_export_tags', username=user.name, _query=q), _export_cols)}</div>
</div>

<p class="lead">${user.fullname}</p>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
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
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
</div>

<%include file="tag_table.mako"/>