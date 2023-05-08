<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-buildings"></i> ${_("Selected companies")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.button(icon='square', color='warning', url=request.route_url('user_clear_selected_companies', username=user.name))}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div class="me-auto">${button.dropdown_order(order_criteria)}</div>
  <div>${button.a_button(icon='download', color='primary', url=request.route_url('user_export_selected_companies', username=user.name, _query=q))}</div>
</div>

<%include file="company_table.mako"/>