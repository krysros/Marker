<%inherit file="layout.mako"/>

<div class="card mt-4 mb-4">
  <div class="card-header">${heading}</div>
  <div class="card-body">

    <form action="${request.current_route_path()}" method="post" accept-charset="utf-8" enctype="multipart/form-data">
      <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
      <div class="mb-3">
        ${form.vcf_file.label(class_="form-label")}
        ${form.vcf_file(class_="form-control" + (" is-invalid" if form.errors.get("vcf_file") else ""), accept=".vcf,text/vcard", required=True)}
        % for error in form.errors.get("vcf_file", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>

      <div class="accordion mb-3" id="vcfRequirementsAccordion">
        <div class="accordion-item">
          <h2 class="accordion-header" id="vcfRequirementsHeading">
            <button
              class="accordion-button collapsed"
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#vcfRequirementsCollapse"
              aria-expanded="false"
              aria-controls="vcfRequirementsCollapse"
            >
              ${_("vCard file requirements")}
            </button>
          </h2>
          <div
            id="vcfRequirementsCollapse"
            class="accordion-collapse collapse"
            aria-labelledby="vcfRequirementsHeading"
            data-bs-parent="#vcfRequirementsAccordion"
          >
            <div class="accordion-body small">
              <ul class="mb-2">
                <li>${_("The file must be a valid vCard 3.0 or 4.0 file (.vcf).")}</li>
                <li>${_("The following fields are imported:")} <code>FN/N</code>, <code>TITLE/ROLE</code>, <code>TEL</code>, <code>EMAIL</code>, <code>ORG</code>, <code>ADR</code>, <code>URL</code>, <code>X-NIP</code>, <code>X-REGON</code>, <code>X-KRS</code>.</li>
                <li>${_("If a company with the same name already exists, the contact will be added to it.")}</li>
                <li>${_("If the contact already exists in the company, you will be redirected to its view.")}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <button type="submit" class="btn btn-success">
        <i class="bi bi-upload"></i> ${_("Import")}
      </button>
    </form>

  </div>
</div>
