<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-people"></i> ${_("Selected contacts")}
    <span class="badge bg-secondary">${counter}</span>
  </h2>
  <div class="d-flex flex-wrap gap-2 justify-content-md-end w-100 w-md-auto">    ${button.deselect_selected(url=request.route_url('user_deselect_contacts', username=user.name), confirm_text=_('Deselect all selected contacts?'))}    ${button.delete_selected(url=request.route_url('user_delete_selected_contacts', username=user.name, _query=q), confirm_text=_("Delete all selected contacts?"))}
    ${button.dropdown_download(url_xlsx=request.route_url('user_export_selected_contacts', username=user.name, _query=q), url_ods=request.route_url('user_export_selected_contacts', username=user.name, _query={**q, 'format': 'ods'}))}
  </div>
  </div>
<hr>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <%include file="contact_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
  <div class="btn-group btn-group-sm ms-auto" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_tags', username=user.name)}">${_("Tags")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_companies', username=user.name)}">${_("Companies")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_projects', username=user.name)}">${_("Projects")}</a>
    <a class="btn btn-primary" href="${request.route_url('user_selected_contacts', username=user.name, _query=q)}">${_("Contacts")}</a>
  </div>
</div>

<%include file="contact_table.mako"/>