<div class="hstack">
  <div class="me-auto">
    <p class="lead">${project.name}</p>
  </div>
  % if project.color != "default":
  <div>
    <p class="lead"><i class="bi bi-circle-fill text-${project.color}"></i></p>
  </div>
  % endif
</div>