<div class="dropdown">
  <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
    <i class="bi bi-filter"></i> ${_("Filter")}
  </button>
  <form class="dropdown-menu p-4">
    % if form.name.data:
      ${form.name(class_="form-control")}
    % endif
    % if form.street.data:
      ${form.street(class_="form-control")}
    % endif
    % if form.postcode.data:
      ${form.postcode(class_="form-control")}
    % endif
    % if form.city.data:
      ${form.city(class_="form-control")}
    % endif
    <div class="mb-3">
      ${form.country.label}
      ${form.country(class_="form-control", **{"hx-get": f"{request.route_url('subdivision')}", "hx-target": "#subdivision"})}
    </div>
    <div class="mb-3">
      ${form.subdivision.label}
      ${form.subdivision(class_="form-control")}
      <small class="text-body-secondary">Ctrl + Click</small>
    </div>
    % if form.website.data:
      ${form.website(class_="form-control")}
    % endif
    <div class="mb-3">
      ${form.color.label}
      ${form.color(class_="form-control")}
    </div>
    <button type="submit" class="btn btn-primary">${_("Submit")}</button>
  </form>
</div>