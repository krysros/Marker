<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-people"></i> ${_("Selected contacts")}
    <span class="badge bg-secondary">
      <div hx-get="${request.route_url('user_selected_contacts_count', username=user.name)}"
           hx-trigger="selectedContactsEvent from:body">
        ${counter}
      </div>
    </span>
  </h2>
  <div class="d-flex flex-wrap gap-2 justify-content-md-end w-100 w-md-auto">
    ${button.delete_selected(url=request.route_url('user_delete_selected_contacts', username=user.name, _query=q), confirm_text=_("Delete all selected contacts?"))}
    <% from marker.utils.export_columns import contact_cols, company_cols, project_cols %>
    <% _export_cols = project_cols(_) if q.get('category') == 'projects' else (company_cols(_) if q.get('category') == 'companies' else contact_cols(_)) %>
    ${button.dropdown_download_cols(request.route_url('user_export_selected_contacts', username=user.name), _export_cols, extra_params=q)}
  </div>
  </div>
<%namespace name="pills" file="/common/pills.mako"/>

<hr>

<%
  companies_q = {**q, 'category': 'companies'}
  projects_q = {**q, 'category': 'projects'}
  
  category_pills = [
      {
          "title": _("Companies"),
          "icon": "buildings",
          "url": request.route_url('user_selected_contacts', username=user.name, _query=companies_q),
          "count": None,
      },
      {
          "title": _("Projects"),
          "icon": "briefcase",
          "url": request.route_url('user_selected_contacts', username=user.name, _query=projects_q),
          "count": None,
      }
  ]
%>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <div class="me-auto">
    ${pills.pills(category_pills, active_url=request.route_url('user_selected_contacts', username=user.name, _query={**q, 'category': q.get('category', 'companies')}))}
  </div>
</div>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <%include file="contact_filter.mako"/>
  <div class="vr mx-1"></div>
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
  <div class="vr mx-1"></div>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts_tags', username=user.name)}"><i class="bi bi-tags"></i> ${_("Tags")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts_companies', username=user.name)}"><i class="bi bi-buildings"></i> ${_("Companies")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts_projects', username=user.name)}"><i class="bi bi-briefcase"></i> ${_("Projects")}</a>
    <a class="btn btn-primary" href="${request.route_url('user_selected_contacts', username=user.name, _query=q)}"><i class="bi bi-people"></i> ${_("Contacts")}</a>
  </div>
</div>

<%include file="contact_table.mako"/>