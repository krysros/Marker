<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="project_pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(project)}</div>
</div>

<%include file="project_lead.mako"/>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('project_similar', dd_filter, project_id=project.id, slug=project.slug)}</div>
</div>

<%include file="project_table.mako"/>