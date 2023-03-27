<%inherit file="layout.mako"/>
<%namespace name="nav_pills" file="nav_pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${nav_pills.project_pill(project)}</div>
</div>

<%include file="project_lead.mako"/>
<%include file="user_table.mako"/>