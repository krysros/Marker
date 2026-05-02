<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-briefcase"></i> ${_("Projects of selected contacts")}
    <span class="badge bg-secondary">${counter}</span>
  </h2>
</div>
<hr>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <%include file="project_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
  <div class="btn-group ms-auto" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts', username=user.name, _query=q)}">${_("Contacts")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts_companies', username=user.name, _query=q)}">${_("Companies")}</a>
    <a class="btn btn-primary" href="${request.route_url('user_selected_contacts_projects', username=user.name, _query=q)}">${_("Projects")}</a>
  </div>
</div>

<%include file="project_table.mako"/>
