<%namespace name="checkbox" file="checkbox.mako"/>

<div class="hstack">
  <div class="me-auto">
    <p class="lead">
      ${checkbox.checkbox(project, selected=request.identity.selected_projects, url=request.route_url('project_check', project_id=project.id, slug=project.slug))}
      &nbsp;${project.name}
      % if project.color:
        <span class="badge text-bg-${project.color}">${_(project.color)}</span>
      % endif
    </p>
  </div>
</div>