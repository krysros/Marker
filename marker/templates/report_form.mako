<%inherit file="layout.mako"/>
<%include file="errors.mako"/> 

<h2><i class="bi bi-bar-chart"></i> Raporty</h2>
<hr>

<div class="card mt-4 mb-4">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form action="${url}" method="post">
      <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
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