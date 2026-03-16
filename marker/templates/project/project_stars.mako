<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div class="me-auto">${pills.pills(project_pills)}</div>
  <div>${button.project_star(project)}</div>
</div>

<%include file="project_lead.mako"/>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="user_table.mako"/>