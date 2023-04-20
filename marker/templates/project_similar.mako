<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(project_pills)}</div>
</div>

<%include file="project_lead.mako"/>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown(dd_filter)}</div>
</div>

<%include file="project_table.mako"/>