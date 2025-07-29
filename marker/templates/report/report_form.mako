<%inherit file="layout.mako"/>

<h2>
  <i class="bi bi-bar-chart"></i> ${_("Reports")}
  <span class="badge bg-secondary">${counter}</span>
</h2>

<hr>

<div class="card mt-4 mb-4">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form action="${url}" method="post">
      <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
      <div class="mb-3">
        ${form.report.label(class_="form-label")}
        ${form.report(class_="form-control" + (" is-invalid" if form.errors.get("report") else ""))}
        % for error in form.errors.get("report", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        <input class="btn btn-primary" id="submit" name="submit" type="submit" value="${_('Show')}">
      </div>
    </form>
  </div>
</div>