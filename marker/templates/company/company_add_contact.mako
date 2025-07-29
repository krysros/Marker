<%inherit file="layout.mako"/>

<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(company_pills, active_url=request.route_url('company_contacts', company_id=company.id, slug=company.slug))}</div>
</div>

<%include file="company_lead.mako"/>

<div class="card mt-4 mb-4">
  <div class="card-header">${heading}</div>
  <div class="card-body">
    <form action="${request.current_route_path()}" method="post">
      <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
      <div class="mb-3">
        ${form.name.label(class_="form-label")}
        ${form.name(class_="form-control" + (" is-invalid" if form.errors.get("name") else ""))}
        % for error in form.errors.get("name", []):
          <div class="invalid-feedback">${error}</div>
        % endfor
      </div>
      <div class="mb-3">
        ${form.role.label(class_="form-label")}
${form.role(class_="form-control" + (" is-invalid" if form.errors.get("role") else ""))}
% for error in form.errors.get("role", []):
  <div class="invalid-feedback">${error}</div>
% endfor
      </div>
      <div class="mb-3">
        ${form.phone.label(class_="form-label")}
${form.phone(class_="form-control" + (" is-invalid" if form.errors.get("phone") else ""))}
% for error in form.errors.get("phone", []):
  <div class="invalid-feedback">${error}</div>
% endfor
      </div>
      <div class="mb-3">
        ${form.email.label(class_="form-label")}
${form.email(class_="form-control" + (" is-invalid" if form.errors.get("email") else ""))}
% for error in form.errors.get("email", []):
  <div class="invalid-feedback">${error}</div>
% endfor
      </div>
      <div class="mb-3">
        <button type="submit" class="btn btn-primary">${_("Submit")}</button>
      </div>
    </form>
  </div>
</div>