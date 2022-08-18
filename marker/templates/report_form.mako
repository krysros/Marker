<%inherit file="layout.mako"/>
<%include file="errors.mako"/> 

<div class="card">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form method="post" action="${url}">
      <div class="mb-3">
        ${form.report.label}
        ${form.report(class_="form-control")}
      </div>
      <div class="mb-3">
        ${form.submit(class_="btn btn-primary")}
      </div>
    </form>
  </div>
</div>