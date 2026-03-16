<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0">
    <i class="bi bi-people"></i> ${_("Selected contacts")}
    <span class="badge bg-secondary">${counter}</span>
  </h2>
  <div class="d-flex flex-wrap gap-2 justify-content-md-end w-100 w-md-auto">
    ${button.delete_selected(url=request.route_url('user_delete_selected_contacts', username=user.name, _query=q), confirm_text=_("Delete all selected contacts?"))}
    ${button.a(icon='download', color='primary', url=request.route_url('user_export_selected_contacts', username=user.name, _query=q))}
  </div>
</div>
<hr>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <%include file="contact_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div class="me-auto">${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="contact_table.mako"/>