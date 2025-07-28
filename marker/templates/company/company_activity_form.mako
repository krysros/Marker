<%inherit file="layout.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(company_pills, active_url=request.route_url('company_projects', company_id=company.id, slug=company.slug))}</div>
</div>

<%include file="company_lead.mako"/>

<div class="card mt-4 mb-4">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form action="${request.current_route_path()}" method="post">
      <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
      <div class="mb-3">
        ${form.name.label}
        ${form.name(class_="form-control" + (" is-invalid" if form.errors.get("name") else ""), list_="projects", autocomplete="off", maxlength="200", **{"hx-get": f"{request.route_url('project_select')}", "hx-target": "#select-list", "hx-swap": "innerHTML", "hx-trigger": "keyup changed delay:250ms"})}
        % for error in form.errors.get("name", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
        <div id="select-list"></div>
      </div>
      <div class="mb-3">
        ${form.stage.label}
        ${form.stage(class_="form-control" + (" is-invalid" if form.errors.get("stage") else ""))}
        % for error in form.errors.get("stage", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        ${form.role.label}
        ${form.role(class_="form-control" + (" is-invalid" if form.errors.get("role") else ""))}
        % for error in form.errors.get("role", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        <button type="submit" class="btn btn-primary">${_("Submit")}</button>
      </div>
    </form>
  </div>
</div>