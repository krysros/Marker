<div class="dropdown">
  <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
    <i class="bi bi-filter"></i> ${_("Filter")}
  </button>
  <form class="dropdown-menu p-4">
    % if form.name.data:
      ${form.name(class_="form-control")}
    % endif
    % if form.role.data:
      ${form.role(class_="form-control")}
    % endif
    % if form.phone.data:
      ${form.phone(class_="form-control")}
    % endif
    % if form.email.data:
      ${form.email(class_="form-control")}
    % endif
    <div class="mb-3">
      ${form.parent.label}
      ${form.parent(class_="form-control")}
    </div>
    <button type="submit" class="btn btn-primary">${_("Submit")}</button>
  </form>
</div>