<%inherit file="layout.mako"/>
<%include file="errors.mako"/>

<div class="card">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form action="${request.current_route_path()}" method="post">
      <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
      <div class="mb-3">
        ${form.name.label}
        ${form.name(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.street.label}
        ${form.street(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.postcode.label}
        ${form.postcode(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.city.label}
        ${form.city(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.state.label}
        ${form.state(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.link.label}
        ${form.link(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.deadline.label}
        ${form.deadline(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.stage.label}
        ${form.stage(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.project_delivery_method.label}
        ${form.project_delivery_method(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.submit(class_="btn btn-primary")}
      </div>
    </form>
  </div>
</div>