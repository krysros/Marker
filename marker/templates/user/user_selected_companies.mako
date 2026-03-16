<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-buildings"></i> ${_("Selected companies")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.delete_selected(url=request.route_url('user_delete_selected_companies', username=user.name, _query=q), confirm_text=_("Delete all selected companies?"))}
    ${button.a(icon='map', color='secondary', url=request.route_url('user_map_selected_companies', username=user.name, _query=q))}
    ${button.a(icon='download', color='primary', url=request.route_url('user_export_selected_companies', username=user.name, _query=q))}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <%include file="company_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
  <div class="btn-group ms-auto" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-primary" href="${request.route_url('user_selected_companies', username=user.name, _query=q)}">${_("Companies")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_companies_contacts', username=user.name, _query=q)}">${_("Contacts")}</a>
  </div>
</div>

<%include file="company_table.mako"/>