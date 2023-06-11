<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-check-square"></i> ${_("Companies")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a_button(icon='map', color='secondary', url=request.route_url('user_map_selected_companies', username=user.name, _query=q))}
    ${button.button(icon='square', color='warning', url=request.route_url('user_clear_selected_companies', username=user.name))}
    ${button.a_button(icon='download', color='primary', url=request.route_url('user_export_selected_companies', username=user.name, _query=q))}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <%include file="company_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div class="me-auto">${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="company_table.mako"/>