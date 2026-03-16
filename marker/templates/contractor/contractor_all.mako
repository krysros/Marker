<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-diagram-3"></i> ${_("Contractors")}
  <span class="badge bg-secondary">${counter}</span>
</h2>

<hr>

<div class="hstack gap-2 mb-4 d-flex flex-wrap ">
  <div class="dropdown">
    <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
      <i class="bi bi-filter"></i> ${_("Filter")}
    </button>
    <form class="dropdown-menu p-4" style="min-width: 420px;" method="get">
      <input type="hidden" name="sort" value="${q.get('sort', 'created_at')}">
      <input type="hidden" name="order" value="${q.get('order', 'desc')}">
      <div class="mb-3">
        <label for="contractor-filter-roles" class="form-label">${_("Role")}</label>
        <select id="contractor-filter-roles" class="form-control" name="role" multiple size="8">
          % for role_key, role_label in available_roles:
          <option value="${role_key}" ${'selected' if role_key in q.get('role', []) else ''}>${role_label}</option>
          % endfor
        </select>
        <small class="text-body-secondary">Ctrl + Click</small>
      </div>
      <div class="mb-3">
        <label for="contractor-filter-tags" class="form-label">${_("Tags")}</label>
        <select id="contractor-filter-tags" class="form-control" name="tag" multiple size="10">
          % for tag_name in available_tags:
          <option value="${tag_name}" ${'selected' if tag_name in q.get('tag', []) else ''}>${tag_name}</option>
          % endfor
        </select>
        <small class="text-body-secondary">Ctrl + Click</small>
      </div>
      <div class="hstack gap-2">
        <button type="submit" class="btn btn-primary">${_("Submit")}</button>
        <a class="btn btn-outline-secondary" href="${request.route_url('contractor_all', _query={'sort': q.get('sort', 'created_at'), 'order': q.get('order', 'desc')})}">${_("Clear")}</a>
      </div>
    </form>
  </div>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="company_table.mako"/>