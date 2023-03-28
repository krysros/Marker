<%inherit file="layout.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.project_pill(project)}</div>
</div>

<%include file="project_lead.mako"/>
<%include file="user_table.mako"/>