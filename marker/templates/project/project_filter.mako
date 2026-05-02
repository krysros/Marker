<div class="dropdown">
  <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
    <i class="bi bi-filter"></i> ${_("Filter")}
  </button>
  <form class="dropdown-menu p-4" style="min-width: 420px;">
    % for tag in q.get("tag", []):
      <input type="hidden" name="tag" value="${tag}">
    % endfor
    % if q.get("view"):
      <input type="hidden" name="view" value="${q.get('view')}">
    % endif
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
      ${form.country.label(class_="form-label")}
      ${form.country(class_="form-control", **{"hx-get": f"{request.route_url('subdivision')}", "hx-target": "#subdivision"})}
    </div>
    <div class="mb-3">
      ${form.subdivision.label(class_="form-label")}
      ${form.subdivision(class_="form-control")}
      <small class="text-body-secondary">Ctrl + Click</small>
    </div>
    % if form.website.data:
      ${form.website(class_="form-control")}
    % endif
    % if form.deadline.data:
      ${form.deadline(class_="form-control")}
    % endif
    <div class="mb-3">
      <label class="form-label">${_("Deadline")}</label>
      <div class="input-group">
        ${form.deadline_from(class_="form-control", placeholder=_("From"))}
        ${form.deadline_to(class_="form-control", placeholder=_("To"))}
      </div>
    </div>
    <div class="mb-3">
      ${form.stage.label(class_="form-label")}
      ${form.stage(class_="form-control")}
    </div>
    <div class="mb-3">
      ${form.delivery_method.label(class_="form-label")}
      ${form.delivery_method(class_="form-control")}
    </div>
    <div class="mb-3">
      <label class="form-label">${_("Usable area [m\u00b2]")}</label>
      <div class="input-group">
        ${form.usable_area_from(class_="form-control", placeholder=_("From"))}
        ${form.usable_area_to(class_="form-control", placeholder=_("To"))}
      </div>
    </div>
    <div class="mb-3">
      <label class="form-label">${_("Cubic volume [m\u00b3]")}</label>
      <div class="input-group">
        ${form.cubic_volume_from(class_="form-control", placeholder=_("From"))}
        ${form.cubic_volume_to(class_="form-control", placeholder=_("To"))}
      </div>
    </div>
    <div class="mb-3">
      ${form.color.label(class_="form-label")}
      ${form.color(class_="form-control")}
    </div>
    <div class="mb-3">
      ${form.status.label(class_="form-label")}
      ${form.status(class_="form-control")}
    </div>
    <div class="mb-3">
      <label class="form-label">${_("Date")}</label>
      <div class="input-group">
        ${form.date_from(class_="form-control", placeholder=_("From"))}
        ${form.date_to(class_="form-control", placeholder=_("To"))}
      </div>
    </div>
    <div class="hstack gap-2">
      <button type="submit" class="btn btn-primary">${_("Submit")}</button>
      <% clear_q = {k: v for k, v in q.items() if k in ('sort', 'order')} %>
      <a class="btn btn-outline-secondary" href="${request.current_route_url(_query=clear_q)}">${_("Clear")}</a>
    </div>
  </form>
</div>