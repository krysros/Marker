<%inherit file="layout.mako"/>
<%namespace name="nav_pills" file="nav_pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${nav_pills.nav_project(project, active_link="watched")}</div>
</div>

<%include file="project_lead.mako"/>
<%include file="user_table.mako"/>