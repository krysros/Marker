<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-people"></i> ${_("Contacts")}
  <span class="badge bg-secondary">${counter}</span>
  <small class="text-body-secondary ms-2">${_("Selected contacts")}</small>
  <div class="float-end">
    ${button.delete_selected(url=request.route_url('user_delete_selected_contacts', username=user.name, _query=q), confirm_text=_("Delete all selected contacts?"))}
    ${button.a(icon='download', color='primary', url=request.route_url('user_export_selected_contacts', username=user.name, _query=q))}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4 d-flex flex-wrap ">
  <%include file="contact_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div class="me-auto">${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="contact_table.mako"/>