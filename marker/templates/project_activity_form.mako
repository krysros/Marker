<%inherit file="layout.mako"/>
<%include file="errors.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(project_pills, active_url=request.route_url('project_companies', project_id=project.id, slug=project.slug))}</div>
</div>

<%include file="project_lead.mako"/>

<div class="card mt-4 mb-4">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form action="${request.current_route_path()}" method="post">
      <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
      <div class="mb-3">
        ${form.name.label}
        ${form.name(class_="form-control", list_="companies", autocomplete="off", maxlength="200", **{"hx-get": f"{request.route_url('company_select')}", "hx-target": "#select-list", "hx-swap": "innerHTML", "hx-trigger": "keyup changed delay:250ms"})}
        <div id="select-list"></div>
      </div>
      <div class="mb-3">
        ${form.stage.label}
        ${form.stage(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.role.label}
        ${form.role(class_="form-control")}
      </div>
      <div class="mb-3">
        <button type="submit" class="btn btn-primary">${_("Submit")}</button>
      </div>
    </form>
  </div>
</div>