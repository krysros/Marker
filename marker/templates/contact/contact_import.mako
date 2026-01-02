<%inherit file="layout.mako"/>

<div id="import-alert" class="alert alert-warning d-none" role="alert">
  Don't close your browser tab. Importing...
</div>

<div class="card mt-4 mb-4">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form action="${request.current_route_path()}" method="post" accept-charset="utf-8" enctype="multipart/form-data">
      <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
      <div class="mb-3">
        ${form.csv_file.label(class_="form-label")}
        ${form.csv_file(class_="form-control" + (" is-invalid" if form.errors.get("csv_file") else ""), accept="text/csv")}
        % for error in form.errors.get("csv_file", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        <button type="submit" class="btn btn-primary" onclick="if (document.querySelector('input[name=csv_file]').files.length > 0) { document.getElementById('import-alert').classList.remove('d-none'); } else { alert('Please select a CSV file'); return false; }">${_("Submit")}</button>
      </div>
    </form>
  </div>
</div>