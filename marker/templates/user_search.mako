<%inherit file="layout.mako"/>
<%include file="errors.mako"/>

<div class="card mt-4 mb-4">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form action="${request.current_route_path()}" method="post">
      <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
      <div class="mb-3">
        ${form.name.label}
        ${form.name(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.fullname.label}
        ${form.fullname(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.email.label}
        ${form.email(class_="form-control")}
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