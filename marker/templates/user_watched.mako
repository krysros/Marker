<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-eye"></i> ${_("Watched")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.button(icon='eye', color='warning', url=request.route_url('user_clear_watched', username=user.name))}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <%include file="project_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div class="me-auto">${button.dropdown_order(order_criteria)}</div>
  <div>${button.a_button(icon='download', color='primary', url=request.route_url('user_export_watched', username=user.name, _query=q))}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="project_table.mako"/>