<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-buildings"></i> ${_("Companies of selected tags")}</small>
  <span class="badge bg-secondary">${counter}</span>
  <!-- export button removed -->
</h2>
<hr>

<div class="d-flex flex-nowrap overflow-x-auto align-items-center gap-2 mb-4 pb-1">
  <%include file="company_filter.mako"/>
  <div class="vr mx-1"></div>
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
  <div class="vr mx-1"></div>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_tags', username=user.name)}"><i class="bi bi-tags"></i> ${_("Tags")}</a>
    <a class="btn btn-primary" href="${request.route_url('user_selected_tags_companies', username=user.name, _query=q)}"><i class="bi bi-buildings"></i> ${_("Companies")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_tags_projects', username=user.name)}"><i class="bi bi-briefcase"></i> ${_("Projects")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_tags_contacts', username=user.name, _query={'category': ''})}" ><i class="bi bi-people"></i> ${_("Contacts")}</a>
  </div>
</div>

<%include file="company_table.mako"/>
