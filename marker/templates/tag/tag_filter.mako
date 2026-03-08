<div class="dropdown">
  <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
    <i class="bi bi-filter"></i> ${_("Filter")}
  </button>
  <form class="dropdown-menu p-4" style="min-width: 200px;">
    % if form.name.data:
      ${form.name()}
    % endif
    <div class="mb-3">
      ${form.category.label(class_="form-label")}
      ${form.category(class_="form-control")}
    </div>
    <button type="submit" class="btn btn-primary">${_("Submit")}</button>
  </form>
</div>
