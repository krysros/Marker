<div class="dropdown">
  <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
    <i class="bi bi-filter"></i> ${_("Filter")}
  </button>
  <form class="dropdown-menu p-4" style="min-width: 420px;">
    % for tag in q.get("tag", []):
      <input type="hidden" name="tag" value="${tag}">
    % endfor
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
      ${form.category.label(class_="form-label")}
      ${form.category(class_="form-control")}
    </div>
    <div class="mb-3">
      ${form.country.label(class_="form-label")}
      ${form.country(class_="form-control", **{"hx-get": f"{request.route_url('subdivision')}", "hx-target": "#subdivision"})}
    </div>
    <div class="mb-3">
      ${form.subdivision.label(class_="form-label")}
      ${form.subdivision(class_="form-control")}
      <small class="text-body-secondary">Ctrl + Click</small>
    </div>
    <div class="mb-3">
      ${form.color.label(class_="form-label")}
      ${form.color(class_="form-control")}
    </div>
    <button type="submit" class="btn btn-primary">${_("Submit")}</button>
  </form>
</div>