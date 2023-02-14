<%namespace name="checkbox" file="checkbox.mako"/>

<div class="hstack">
  <div class="me-auto">
    <p class="lead">
      ${checkbox.check_project(project)}
      &nbsp;${project.name}
    </p>
  </div>
</div>