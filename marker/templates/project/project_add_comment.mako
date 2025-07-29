<%inherit file="layout.mako"/>

<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(project_pills, active_url=request.route_url('project_comments', project_id=project.id, slug=project.slug))}</div>
</div>

<%include file="project_lead.mako"/>

<div class="card mt-4 mb-4">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form action="${request.current_route_path()}" method="post">
      <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
      <div class="mb-3">
        ${form.comment.label(class_="form-label")}
        ${form.comment(class_="form-control" + (" is-invalid" if form.errors.get("comment") else ""))}
        % for error in form.errors.get("comment", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
        <div id="select-list"></div>
      </div>
      <div class="mb-3">
        <button type="submit" class="btn btn-primary">${_("Submit")}</button>
      </div>
    </form>
  </div>
</div>