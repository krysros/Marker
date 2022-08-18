<%inherit file="layout.mako"/>
<%include file="errors.mako"/>

<ul class="nav nav-tabs">
  <li class="nav-item">
    <a class="nav-link" href="${request.route_url('account', username=request.identity.name)}">Konto</a>
  </li>
  <li class="nav-item">
    <a class="nav-link active" href="${request.route_url('password', username=request.identity.name)}">Hasło</a>
  </li>
</ul>

<div class="card">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form method="post" action="${request.current_route_path()}">
      <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
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