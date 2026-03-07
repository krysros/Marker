<%inherit file="layout.mako"/>

<div id="import-alert" class="alert alert-warning htmx-indicator position-fixed top-0 start-50 translate-middle-x mt-3" role="alert" style="z-index: 1080;">
  ${_("Don't close your browser tab. Importing...")}
</div>

<div class="card mt-4 mb-4">
  <div class="card-header">${heading}</div>
  <div class="card-body">

    <form action="${request.current_route_path()}" method="post" accept-charset="utf-8" enctype="multipart/form-data" hx-boost="true" hx-indicator="#import-alert">
      <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
      <div class="mb-3">
        ${form.csv_file.label(class_="form-label")}
        ${form.csv_file(class_="form-control" + (" is-invalid" if form.errors.get("csv_file") else ""), accept="text/csv", required=True)}
        % for error in form.errors.get("csv_file", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="accordion mb-3" id="csvRequirementsAccordion">
        <div class="accordion-item">
          <h2 class="accordion-header" id="csvRequirementsHeading">
            <button
              class="accordion-button collapsed"
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#csvRequirementsCollapse"
              aria-expanded="false"
              aria-controls="csvRequirementsCollapse"
            >
              ${_("CSV file requirements")}
            </button>
          </h2>
          <div
            id="csvRequirementsCollapse"
            class="accordion-collapse collapse"
            aria-labelledby="csvRequirementsHeading"
            data-bs-parent="#csvRequirementsAccordion"
          >
            <div class="accordion-body small">
              <ul class="mb-2">
                <li>${_("The file must be UTF-8 encoded and comma-separated. Other separators are not allowed.")}</li>
                <li>${_("To import contacts, you need to export them from Google Contacts in CSV format. Make sure to select the Google CSV format when exporting.")}</li>
                <li>${_("Contacts without a company (Organization Name) will not be imported.")}</li>
                <li>${_("The file must include at least the following columns: ")}</li>
              </ul>
              <ul class="mb-2">
                <li><code>Organization Name</code> / <code>Organization 1 - Name</code></li>
                <li><code>First Name</code> / <code>Given Name</code></li>
                <li><code>E-mail 1 - Value</code></li>
                <li><code>Phone 1 - Value</code></li>
                <li><code>Labels</code> / <code>Group Membership</code></li>
              </ul>
              <p class="mb-0">
                ${_("For more information on the required CSV structure, please refer to the Google Contacts help page: ")}
                <a href="https://support.google.com/contacts/answer/15147365" target="_blank" rel="noopener noreferrer">https://support.google.com/contacts/answer/15147365</a>.
              </p>
            </div>
          </div>
        </div>
      </div>
      <div class="mb-3">
        <button type="submit" class="btn btn-primary">${_("Submit")}</button>
      </div>
    </form>
  </div>
</div>