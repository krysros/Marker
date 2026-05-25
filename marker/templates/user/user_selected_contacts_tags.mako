<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-tags"></i> ${_("Tags of selected contacts")}
  <span class="badge bg-secondary">${counter}</span>
</h2>
<hr>

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
  <div class="vr mx-1"></div>
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
  <div class="vr mx-1"></div>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-primary" href="${request.route_url('user_selected_contacts_tags', username=user.name, _query=q)}"><i class="bi bi-tags"></i> ${_("Tags")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts_companies', username=user.name)}"><i class="bi bi-buildings"></i> ${_("Companies")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts_projects', username=user.name)}"><i class="bi bi-briefcase"></i> ${_("Projects")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts', username=user.name)}"><i class="bi bi-people"></i> ${_("Contacts")}</a>
  </div>
</div>

<%include file="tag_table.mako"/>
