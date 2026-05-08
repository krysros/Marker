<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-people"></i> ${_("Selected contacts")}
    <span class="badge bg-secondary">${counter}</span>
  </h2>
  <div class="d-flex flex-wrap gap-2 justify-content-md-end w-100 w-md-auto">
    ${button.delete_selected(url=request.route_url('user_delete_selected_contacts', username=user.name, _query=q), confirm_text=_("Delete all selected contacts?"))}
    <% from marker.utils.export_columns import contact_cols, company_cols, project_cols %>
    <% _export_cols = project_cols(_) if q.get('category') == 'projects' else (company_cols(_) if q.get('category') == 'companies' else contact_cols(_)) %>
    ${button.dropdown_download_cols(request.route_url('user_export_selected_contacts', username=user.name), _export_cols, extra_params=q)}
  </div>
  </div>
<hr>

<div class="d-flex flex-nowrap overflow-x-auto align-items-center gap-2 mb-4 pb-1">
  <%include file="contact_filter.mako"/>
  <div class="vr mx-1"></div>
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
</div>

<%include file="contact_table.mako"/>