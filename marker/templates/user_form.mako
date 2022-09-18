<%include file="navbar.mako"/>
<%include file="errors.mako"/>

<div class="card">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form hx-post="${request.current_route_path()}" hx-target="#main-container">
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
        ${form.password.label}
        ${form.password(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.submit(class_="btn btn-primary")}
      </div>
    </form>
  </div>
</div>