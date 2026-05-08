<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <div class="me-auto">${pills.pills(project_pills)}</div>
  <div>${button.project_star(project)}</div>
</div>

<%include file="project_lead.mako"/>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
</div>

<%include file="user_table.mako"/>