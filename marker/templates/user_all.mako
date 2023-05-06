<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-person-circle"></i> ${_("Users")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a_button(icon='search', color='primary', url=request.route_url('user_search'))}
    ${button.a_button(icon='plus-lg', color='success', url=request.route_url('user_add'))}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <div class="dropdown">
    <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
      <i class="bi bi-filter"></i> ${_("Filter")}
    </button>
    <form class="dropdown-menu p-4">
      ${form.name(class_="form-control")}
      ${form.fullname(class_="form-control")}
      ${form.email(class_="form-control")}
      <div class="mb-3">
        ${form.role.label}
        ${form.role(class_="form-control")}
      </div>
      <input class="btn btn-primary" id="submit" name="submit" type="submit" value="${_('Submit')}">
    </form>
  </div>
  <div>${button.dropdown(dd_sort)}</div>
  <div>${button.dropdown(dd_order)}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="user_table.mako"/>