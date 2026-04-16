<%inherit file="layout.mako"/>

<div class="card mt-4 mb-4">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form action="${request.current_route_path()}" method="post">
      <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
      <div class="mb-3">
        <label for="company-name" class="form-label">${_("Company")}</label>
        <input type="text" id="company-name" class="form-control" placeholder="${company.name}" disabled>
      </div>
      <div class="mb-3">
        <label for="project-name" class="form-label">${_("Project")}</label>
        <input type="text" id="project-name" class="form-control" placeholder="${project.name}" disabled>
      </div>
      <div class="mb-3">
        ${form.stage.label(class_="form-label")}
        ${form.stage(class_="form-control" + (" is-invalid" if form.errors.get("stage") else ""))}
        % for error in form.errors.get("stage", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        ${form.role.label(class_="form-label")}
        ${form.role(class_="form-control" + (" is-invalid" if form.errors.get("role") else ""))}
        % for error in form.errors.get("role", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        ${form.currency.label(class_="form-label")}
        ${form.currency(class_="form-control" + (" is-invalid" if form.errors.get("currency") else ""))}
        % for error in form.errors.get("currency", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        ${form.value_net.label(class_="form-label")}
        ${form.value_net(class_="form-control" + (" is-invalid" if form.errors.get("value_net") else ""))}
        % for error in form.errors.get("value_net", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        ${form.value_gross.label(class_="form-label")}
        ${form.value_gross(class_="form-control" + (" is-invalid" if form.errors.get("value_gross") else ""))}
        % for error in form.errors.get("value_gross", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        <button type="submit" class="btn btn-primary">${_("Submit")}</button>
      </div>
    </form>
  </div>
</div>