<%include file="navbar.mako"/>
<%include file="errors.mako"/>

<div class="card">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form hx-post="${request.current_route_path()}" hx-target="#main-container">
      <div class="mb-3">
        ${form.comment.label}
        ${form.comment(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.submit(class_="btn btn-primary")}
      </div>
    </form>
  </div>
</div>