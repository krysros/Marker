<%def name="preserve_params(exclude)">
<%
  skip = set(exclude)
%>
% for k, v in q.items():
  % if k not in skip:
    % if isinstance(v, list):
      % for item in v:
        <input type="hidden" name="${k}" value="${item}">
      % endfor
    % elif v is not None and str(v) != '':
      <input type="hidden" name="${k}" value="${v}">
    % endif
  % endif
% endfor
</%def>

<div class="dropdown">
  <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
    % if q.get('country') or q.get('subdivision'):
      <i class="bi bi-geo-alt-fill"></i>
    % else:
      <i class="bi bi-geo-alt"></i>
    % endif
    ${_("Location")}
  </button>
  <form class="dropdown-menu p-3" style="min-width: 300px;">
    ${preserve_params({'country', 'subdivision'})}
    <div class="mb-3">
      ${form.country.label(class_="form-label")}
      ${form.country(class_="form-control", **{"hx-get": f"{request.route_url('subdivision')}", "hx-target": "#subdivision"})}
    </div>
    <div class="mb-3">
      ${form.subdivision.label(class_="form-label")}
      ${form.subdivision(class_="form-control")}
      <small class="text-body-secondary">Ctrl + Click</small>
    </div>
    <div class="hstack gap-2">
      <button type="submit" class="btn btn-primary btn-sm">${_("Submit")}</button>
      <% clear_q = {k: v for k, v in q.items() if k not in ('country', 'subdivision')} %>
      <a class="btn btn-outline-secondary btn-sm" href="${request.current_route_url(_query=clear_q)}">${_("Clear")}</a>
    </div>
  </form>
</div>

<div class="dropdown">
  <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
    % if q.get('object_category') or q.get('stage') or q.get('delivery_method') or q.get('status'):
      <i class="bi bi-tag-fill"></i>
    % else:
      <i class="bi bi-tag"></i>
    % endif
    ${_("Category")}
  </button>
  <form class="dropdown-menu p-3" style="min-width: 300px; max-height: 480px; overflow-y: auto;">
    ${preserve_params({'object_category', 'stage', 'delivery_method', 'status'})}
    <div class="mb-3">
      ${form.object_category.label(class_="form-label")}
      ${form.object_category(class_="form-control")}
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
      ${form.status.label(class_="form-label")}
      ${form.status(class_="form-control")}
    </div>
    <div class="hstack gap-2">
      <button type="submit" class="btn btn-primary btn-sm">${_("Submit")}</button>
      <% clear_q = {k: v for k, v in q.items() if k not in ('object_category', 'stage', 'delivery_method', 'status')} %>
      <a class="btn btn-outline-secondary btn-sm" href="${request.current_route_url(_query=clear_q)}">${_("Clear")}</a>
    </div>
  </form>
</div>

<div class="dropdown">
  <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
    % if q.get('color'):
      <i class="bi bi-palette-fill"></i>
    % else:
      <i class="bi bi-palette"></i>
    % endif
    ${_("Color")}
  </button>
  <form class="dropdown-menu p-3" style="min-width: 220px;">
    ${preserve_params({'color'})}
    <div class="mb-3">
      ${form.color.label(class_="form-label")}
      ${form.color(class_="form-control")}
    </div>
    <div class="hstack gap-2">
      <button type="submit" class="btn btn-primary btn-sm">${_("Submit")}</button>
      <% clear_q = {k: v for k, v in q.items() if k != 'color'} %>
      <a class="btn btn-outline-secondary btn-sm" href="${request.current_route_url(_query=clear_q)}">${_("Clear")}</a>
    </div>
  </form>
</div>

<div class="dropdown">
  <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
    % if q.get('usable_area_from') or q.get('usable_area_to') or q.get('cubic_volume_from') or q.get('cubic_volume_to'):
      <i class="bi bi-rulers"></i>
    % else:
      <i class="bi bi-rulers"></i>
    % endif
    ${_("Parameters")}
  </button>
  <form class="dropdown-menu p-3" style="min-width: 300px;">
    ${preserve_params({'usable_area_from', 'usable_area_to', 'cubic_volume_from', 'cubic_volume_to'})}
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
    <div class="hstack gap-2">
      <button type="submit" class="btn btn-primary btn-sm">${_("Submit")}</button>
      <% clear_q = {k: v for k, v in q.items() if k not in ('usable_area_from', 'usable_area_to', 'cubic_volume_from', 'cubic_volume_to')} %>
      <a class="btn btn-outline-secondary btn-sm" href="${request.current_route_url(_query=clear_q)}">${_("Clear")}</a>
    </div>
  </form>
</div>

<div class="dropdown">
  <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
    % if q.get('deadline_from') or q.get('deadline_to') or q.get('date_from') or q.get('date_to'):
      <i class="bi bi-calendar-fill"></i>
    % else:
      <i class="bi bi-calendar"></i>
    % endif
    ${_("Date")}
  </button>
  <form class="dropdown-menu p-3" style="min-width: 300px;">
    ${preserve_params({'deadline_from', 'deadline_to', 'date_from', 'date_to'})}
    <div class="mb-3">
      <label class="form-label">${_("Deadline")}</label>
      <div class="input-group">
        ${form.deadline_from(class_="form-control", placeholder=_("From"))}
        ${form.deadline_to(class_="form-control", placeholder=_("To"))}
      </div>
    </div>
    <div class="mb-3">
      <label class="form-label">${_("Date")}</label>
      <div class="input-group">
        ${form.date_from(class_="form-control", placeholder=_("From"))}
        ${form.date_to(class_="form-control", placeholder=_("To"))}
      </div>
    </div>
    <div class="hstack gap-2">
      <button type="submit" class="btn btn-primary btn-sm">${_("Submit")}</button>
      <% clear_q = {k: v for k, v in q.items() if k not in ('deadline_from', 'deadline_to', 'date_from', 'date_to')} %>
      <a class="btn btn-outline-secondary btn-sm" href="${request.current_route_url(_query=clear_q)}">${_("Clear")}</a>
    </div>
  </form>
</div>