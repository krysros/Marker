<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-check-square"></i> <i class="bi bi-briefcase"></i> ${_("Projects")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a(icon='download', color='primary', url=request.route_url('user_export_selected_tags', username=user.name, _query={**q, 'category': 'projects'}))}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <%include file="project_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
  <div class="btn-group ms-auto" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_tags', username=user.name)}">${_("Tags")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_tags_companies', username=user.name)}">${_("Companies")}</a>
    <a class="btn btn-primary" href="${request.route_url('user_selected_tags_projects', username=user.name, _query=q)}">${_("Projects")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_tags_contacts', username=user.name, _query={'category': ''})}">${_("Contacts")}</a>
  </div>
</div>

<%include file="project_table.mako"/>
