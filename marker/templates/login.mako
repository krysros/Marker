<%inherit file="layout.mako"/>
<%include file="errors.mako"/>

<div class="card">
  <div class="card-header">${heading}</div>
    <div class="card-body">
    <form action="${url}" method="post">
      <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
      <input type="hidden" name="next" value="${next_url}">
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