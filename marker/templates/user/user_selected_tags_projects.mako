<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-briefcase"></i> ${_("Projects of selected tags")}
  <span class="badge bg-secondary">${counter}</span>
  <!-- export button removed -->
</h2>
<hr>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <%include file="project_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
  <div class="btn-group btn-group-sm ms-auto" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_tags', username=user.name)}">${_("Tags")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_tags_companies', username=user.name)}">${_("Companies")}</a>
    <a class="btn btn-primary" href="${request.route_url('user_selected_tags_projects', username=user.name, _query=q)}">${_("Projects")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_tags_contacts', username=user.name, _query={'category': ''})}">${_("Contacts")}</a>
  </div>
</div>

<%include file="project_table.mako"/>
