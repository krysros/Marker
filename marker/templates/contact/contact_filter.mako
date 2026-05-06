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
    % if q.get('category'):
      <i class="bi bi-tag-fill"></i>
    % else:
      <i class="bi bi-tag"></i>
    % endif
    ${_("Category")}
  </button>
  <form class="dropdown-menu p-3" style="min-width: 240px;">
    ${preserve_params({'category'})}
    <div class="mb-3">
      ${form.category.label(class_="form-label")}
      ${form.category(class_="form-control")}
    </div>
    <div class="hstack gap-2">
      <button type="submit" class="btn btn-primary btn-sm">${_("Submit")}</button>
      <% clear_q = {k: v for k, v in q.items() if k != 'category'} %>
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
    % if q.get('date_from') or q.get('date_to'):
      <i class="bi bi-calendar-fill"></i>
    % else:
      <i class="bi bi-calendar"></i>
    % endif
    ${_("Date")}
  </button>
  <form class="dropdown-menu p-3" style="min-width: 280px;">
    ${preserve_params({'date_from', 'date_to'})}
    <div class="mb-3">
      <label class="form-label">${_("Date")}</label>
      <div class="input-group">
        ${form.date_from(class_="form-control", placeholder=_("From"))}
        ${form.date_to(class_="form-control", placeholder=_("To"))}
      </div>
    </div>
    <div class="hstack gap-2">
      <button type="submit" class="btn btn-primary btn-sm">${_("Submit")}</button>
      <% clear_q = {k: v for k, v in q.items() if k not in ('date_from', 'date_to')} %>
      <a class="btn btn-outline-secondary btn-sm" href="${request.current_route_url(_query=clear_q)}">${_("Clear")}</a>
    </div>
  </form>
</div>