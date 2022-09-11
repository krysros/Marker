<%include file="navbar.mako"/>
<%include file="errors.mako"/>

<ul class="nav nav-tabs">
  <li class="nav-item">
    <a class="nav-link active" role="button" href="#" hx-get="${request.route_url('account', username=request.identity.name)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Konto</a>
  </li>
  <li class="nav-item">
    <a class="nav-link" role="button" href="#" hx-get="${request.route_url('password', username=request.identity.name)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Hasło</a>
  </li>
</ul>

<div class="card">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form hx-post="${request.current_route_path()}" hx-target="#main-container">
      <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
      <div class="mb-3">
        ${form.fullname.label}
        ${form.fullname(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.email.label}
        ${form.email(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.submit(class_="btn btn-primary")}
      </div>
    </form>
  </div>
</div>