<%inherit file="layout.mako"/>
<%include file="errors.mako"/>

<div class="card mt-4 mb-4">
  <div class="card-header">
    <ul class="nav nav-tabs card-header-tabs">
      <li class="nav-item">
        <a class="nav-link" role="button" href="${request.route_url('account', username=request.identity.name)}">${_("Account")}</a>
      </li>
      <li class="nav-item">
        <a class="nav-link active" role="button" href="${request.route_url('password', username=request.identity.name)}">${_("Password")}</a>
      </li>
    </ul>
  </div>
  <div class="card-body">
    <form action="${request.current_route_path()}" method="post">
      <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
      <div class="mb-3">
        ${form.password.label}
        ${form.password(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.confirm.label}
        ${form.confirm(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.submit(class_="btn btn-primary")}
      </div>
    </form>
  </div>
</div>