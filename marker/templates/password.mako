<%inherit file="layout.mako"/>  

<ul class="nav nav-tabs">
  <li class="nav-item">
    <a class="nav-link" href="${request.route_url('account', username=request.identity.username)}">Konto</a>
  </li>
  <li class="nav-item">
    <a class="nav-link active" href="${request.route_url('password', username=request.identity.username)}">Hasło</a>
  </li>
</ul>

<div class="card">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    ${rendered_form | n}
  </div>
</div>