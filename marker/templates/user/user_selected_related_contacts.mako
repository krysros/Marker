<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<%
  switch_mode = context.get("switch_mode", "")
%>

</span>
% if switch_mode == "selected_companies":
  <h2>
    <i class="bi bi-people"></i> ${_("Contacts of selected companies")}
    <span class="badge bg-secondary">${counter}</span>
  </h2>
% elif switch_mode == "selected_projects":
  <h2>
    <i class="bi bi-people"></i> ${_("Contacts of selected projects")}
  </h2>
% elif switch_mode == "selected_tags":
  <% selected_category = q.get("category", "") %>
  <h2>
    % if selected_category == "companies":
      <i class="bi bi-people"></i> ${_("Contacts of companies from selected tags")}
    % elif selected_category == "projects":
      <i class="bi bi-people"></i> ${_("Contacts of projects from selected tags")}
    % else:
      <i class="bi bi-people"></i> ${_("Contacts of selected tags")}
    % endif
    <span class="badge bg-secondary">${counter}</span>
  </h2>
% else:
  <h2>
    <i class="bi bi-people"></i> ${heading}
    <span class="badge bg-secondary">${counter}</span>
  </h2>
% endif
</h2>
<hr>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <%include file="contact_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
  % if switch_mode == "selected_companies":
  <div class="btn-group ms-auto" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-outline-primary" href="${switch_url}">${_("Companies")}</a>
    <a class="btn btn-primary" href="${request.route_url('user_selected_companies_contacts', username=user.name, _query=q)}">${_("Contacts")}</a>
  </div>
  % elif switch_mode == "selected_projects":
  <div class="btn-group ms-auto" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-outline-primary" href="${switch_url}">${_("Projects")}</a>
    <a class="btn btn-primary" href="${request.route_url('user_selected_projects_contacts', username=user.name, _query=q)}">${_("Contacts")}</a>
  </div>
  % elif switch_mode == "selected_tags":
  <% selected_category = q.get("category", "") %>
  <div class="btn-group ms-auto" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-outline-primary" href="${switch_url}">${_("Tags")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_tags_companies', username=user.name)}">${_("Companies")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_tags_projects', username=user.name)}">${_("Projects")}</a>
    <a class="btn ${'btn-primary' if selected_category == '' else 'btn-outline-primary'}" href="${request.route_url('user_selected_tags_contacts', username=user.name, _query={**q, 'category': ''})}">${_("Contacts")}</a>
  </div>
  % else:
  <div class="ms-auto">
    ${button.a(icon=switch_icon, color='secondary', url=switch_url)}
  </div>
  % endif
</div>

<%include file="contact_table.mako"/>
