<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-people"></i> ${_("Contacts")}
  <span class="badge bg-secondary"><div hx-get="${request.route_url('contact_count')}" hx-trigger="contactEvent from:body">${counter}</div></span>
  <div class="float-end">
    ${button.a_button(icon='search', color='primary', url=request.route_url('contact_search'))}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <div class="dropdown">
    <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
      <i class="bi bi-filter"></i> ${_("Filter")}
    </button>
    <form class="dropdown-menu p-4">
      % if form.name.data:
        ${form.name(class_="form-control")}
      % endif
      % if form.role.data:
        ${form.role(class_="form-control")}
      % endif
      % if form.phone.data:
        ${form.phone(class_="form-control")}
      % endif
      % if form.email.data:
        ${form.email(class_="form-control")}
      % endif
      <div class="mb-3">
        ${form.parent.label}
        ${form.parent(class_="form-control")}
      </div>
      <button type="submit" class="btn btn-primary">${_("Submit")}</button>
    </form>
  </div>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="contact_table.mako"/>