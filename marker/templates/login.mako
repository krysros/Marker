<%inherit file="layout.mako"/>
<%include file="errors.mako"/>

<div class="card">
  <div class="card-header">${heading}</div>
    <div class="card-body">
    <form method="post" action="${url}">
      <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
      <div class="mb-3">
        ${form.username.label}
        ${form.username(class_="form-control")}
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