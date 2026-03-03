<%inherit file="layout.mako"/>

<div id="import-alert" class="alert alert-warning htmx-indicator position-fixed top-0 start-50 translate-middle-x mt-3" role="alert" style="z-index: 1080;">
  Don't close your browser tab. Importing...
</div>

<div class="card mt-4 mb-4">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <div class="alert alert-info" role="alert">
      <strong>${_("Required CSV structure (Google Contacts)")}</strong>
      <div class="small mt-2">${_("The file must include at least the following columns:")}</div>
      <ul class="small mb-0 mt-2">
        <li><code>Organization Name</code></li>
        <li><code>First Name</code></li>
        <li><code>E-mail 1 - Value</code></li>
        <li><code>Phone 1 - Value</code></li>
        <li><code>Labels</code></li>
        <li><code>Notes</code></li>
      </ul>
    </div>

    <form action="${request.current_route_path()}" method="post" accept-charset="utf-8" enctype="multipart/form-data" hx-boost="true" hx-indicator="#import-alert">
      <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
      <div class="mb-3">
        ${form.csv_file.label(class_="form-label")}
        ${form.csv_file(class_="form-control" + (" is-invalid" if form.errors.get("csv_file") else ""), accept="text/csv", required=True)}
        % for error in form.errors.get("csv_file", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        <button type="submit" class="btn btn-primary">${_("Submit")}</button>
      </div>
    </form>
  </div>
</div>