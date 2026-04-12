<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div class="me-auto">${pills.pills(user_pills, active_url=request.route_url('user_tags', username=user.name))}</div>
  <div>${button.a(icon='download', color='primary', title='XLSX', url=request.route_url('user_export_tags', username=user.name, _query=q))}</div>
  <div>${button.a(icon='download', color='outline-primary', title='ODS', url=request.route_url('user_export_tags', username=user.name, _query={**q, 'format': 'ods'}))}</div>
</div>

<p class="lead">${user.fullname}</p>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div class="dropdown">
    <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
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
</div>

<%include file="tag_table.mako"/>