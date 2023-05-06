<%inherit file="layout.mako"/>
<%include file="errors.mako"/>

<div class="card mt-4 mb-4">
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
        <input class="btn btn-primary" id="submit" name="submit" type="submit" value="${_('Log in')}">
      </div>
    </form>
  </div>
</div>