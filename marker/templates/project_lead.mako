<div class="hstack">
  <div class="me-auto">
    <p class="lead">
      % if project in request.identity.selected_projects:
      <input class="form-check-input"
            id="mark"
            type="checkbox"
            value="${project.id}"
            autocomplete="off"
            checked
            hx-post="${request.route_url('project_check', project_id=project.id)}"
            hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
            hx-trigger="click"
            hx-swap="none">
      % else:
      <input class="form-check-input"
            id="mark"
            type="checkbox"
            value="${project.id}"
            autocomplete="off"
            hx-post="${request.route_url('project_check', project_id=project.id)}"
            hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
            hx-trigger="click"
            hx-swap="none">
      % endif
      &nbsp;${project.name}
    </p>
  </div>
</div>