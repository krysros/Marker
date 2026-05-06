<%def name="a(title=None, icon=None, color=None, size=None, url='#')">
  <a class="btn${' btn-' + color if color else ''}${' btn-' + size if size else ''}" role="button" href="${url}">
  % if icon:
    <i class="bi bi-${icon}"></i>
  % endif
  % if title:
    ${title}
  % endif
  </a>
</%def>

<%def name="button(title=None, icon=None, color=None, size=None, url='#')">
  % if request.is_authenticated and request.identity.role == 'editor' or 'admin':
    <button type="button" class="btn${' btn-' + color if color else ''}${' btn-' + size if size else ''}" hx-post="${url}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-confirm='${_("Are you sure?")}'>
  % else:
    <button type="button" class="btn${' btn-' + color if color else ''}${' btn-' + size if size else ''}" disabled>
  % endif
  % if icon:
    <i class="bi bi-${icon}"></i>
  % endif
  % if title:
    ${title}
  % endif
  </button>
</%def>

<%def name="del_card(title=None, icon=None, color=None, size=None, url='#')">
  % if request.is_authenticated and request.identity.role == 'editor' or 'admin':
    <button type="button" class="btn${' btn-' + color if color else ''}${' btn-' + size if size else ''}" hx-post="${url}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-confirm='${_("Are you sure?")}' hx-target="closest .card" hx-swap="outerHTML swap:1s">
  % else:
    <button type="button" class="btn${' btn-' + color if color else ''}${' btn-' + size if size else ''}" disabled>
  % endif
  % if icon:
    <i class="bi bi-${icon}"></i>
  % endif
  % if title:
    ${title}
  % endif
  </button>
</%def>

<%def name="del_row(title=None, icon=None, color=None, size=None, url='#')">
  % if request.is_authenticated and request.identity.role == 'editor' or 'admin':
    <button type="button" class="btn${' btn-' + color if color else ''}${' btn-' + size if size else ''}" hx-post="${url}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-confirm='${_("Are you sure?")}' hx-target="closest tr" hx-swap="outerHTML swap:1s">
  % else:
    <button type="button" class="btn${' btn-' + color if color else ''}${' btn-' + size if size else ''}" disabled>
  % endif
  % if icon:
    <i class="bi bi-${icon}"></i>
  % endif
  % if title:
    ${title}
  % endif
  </button>
</%def>

<%def name="delete_selected(icon='trash', color='danger', size=None, url='#', confirm_text=None)">
  % if request.is_authenticated and request.identity.role == 'editor' or 'admin':
    <button type="button" class="btn btn-${color}${' btn-' + size if size else ''}" hx-post="${url}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-confirm='${confirm_text or _("Are you sure?")}'>
  % else:
    <button type="button" class="btn btn-${color}${' btn-' + size if size else ''}" disabled>
  % endif
    <i class="bi bi-${icon}"></i>
  </button>
</%def>

<%def name="deselect_selected(icon='x-circle', color='secondary', size=None, url='#', confirm_text=None)">
  % if request.is_authenticated and request.identity.role == 'editor' or 'admin':
    <button type="button" class="btn btn-${color}${' btn-' + size if size else ''}" hx-post="${url}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-confirm='${confirm_text or _("Are you sure?")}'>
  % else:
    <button type="button" class="btn btn-${color}${' btn-' + size if size else ''}" disabled>
  % endif
    <i class="bi bi-${icon}"></i>
  </button>
</%def>

<%def name="company_star(company, size=None)">
<button class="btn btn-primary${' btn-' + size if size else ''}" hx-post="${request.route_url('company_star', company_id=company.id, slug=company.slug)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-target="#company-star-${company.id}" hx-swap="innerHTML">
  <div id="company-star-${company.id}">
  % if company in request.identity.companies_stars:
    <i class="bi bi-star-fill"></i>
  % else:
    <i class="bi bi-star"></i>
  % endif
  </div>
</button>
</%def>

<%def name="project_star(project, size=None)">
<button class="btn btn-primary${' btn-' + size if size else ''}" hx-post="${request.route_url('project_star', project_id=project.id, slug=project.slug)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-target="#project-star-${project.id}" hx-swap="innerHTML">
  <div id="project-star-${project.id}">
  % if project in request.identity.projects_stars:
    <i class="bi bi-star-fill"></i>
  % else:
    <i class="bi bi-star"></i>
  % endif
  </div>
</button>
</%def>

<%def name="dropdown_sort(items)">
<div class="btn-group">
  <div class="dropdown">
    <a class="btn btn-sm btn-secondary dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
      % if q["order"] == "asc":
        <i class="bi bi-sort-alpha-down"></i>
      % else:
        <i class="bi bi-sort-alpha-down-alt"></i>
      % endif
      ${_("Sort")}
    </a>
    <ul class="dropdown-menu">
      % for k, v in items.items():
      <li>
        <a class="dropdown-item" role="button" href="${request.current_route_url(_query={**q, 'sort': k})}">
          % if k == q["sort"]:
            <strong>${v}</strong>
          % else:
            ${v}
          % endif
        </a>
      </li>
      % endfor
    </ul>
  </div>
</div>
</%def>

<%def name="dropdown_import(url_csv='#', url_vcard='#')">
<div class="btn-group">
  <div class="dropdown">
    <a class="btn btn-success dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
      <i class="bi bi-upload"></i>
    </a>
    <ul class="dropdown-menu dropdown-menu-end">
      <li><a class="dropdown-item" href="${url_csv}">CSV</a></li>
      <li><a class="dropdown-item" href="${url_vcard}">vCard</a></li>
    </ul>
  </div>
</div>
</%def>

<%def name="dropdown_download(url_xlsx='#', url_ods='#')">
<div class="btn-group">
  <div class="dropdown">
    <a class="btn btn-primary dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
      <i class="bi bi-download"></i>
    </a>
    <ul class="dropdown-menu dropdown-menu-end">
      <li><a class="dropdown-item" href="${url_xlsx}">XLSX</a></li>
      <li><a class="dropdown-item" href="${url_ods}">ODS</a></li>
    </ul>
  </div>
</div>
</%def>

<%def name="dropdown_download_cols(base_url, columns)">
<%
  import json as _json
  uid = abs(hash(base_url)) % 100000
%>
<div class="dropdown">
  <button class="btn btn-primary dropdown-toggle" type="button"
          data-bs-toggle="dropdown" data-bs-auto-close="outside"
          aria-expanded="false">
    <i class="bi bi-download"></i>
  </button>
  <div class="dropdown-menu dropdown-menu-end p-2" style="min-width:260px">
    <form id="export-form-${uid}" method="get" action="${base_url}">
      <div class="mb-2 fw-semibold small">${_("Columns")}</div>
      <div style="max-height:260px;overflow-y:auto">
        % for col in columns:
        <div class="form-check form-check-sm">
          <input class="form-check-input" type="checkbox" name="columns"
                 value="${col}" checked id="ec-${uid}-${loop.index}">
          <label class="form-check-label small" for="ec-${uid}-${loop.index}">${col}</label>
        </div>
        % endfor
      </div>
      <hr class="my-2">
      <div class="mb-2 fw-semibold small">${_("Format")}</div>
      <div class="btn-group btn-group-sm w-100" role="group">
        <input type="radio" class="btn-check" name="format" value="xlsx" id="fmt-xlsx-${uid}" checked autocomplete="off">
        <label class="btn btn-outline-primary" for="fmt-xlsx-${uid}">XLSX</label>
        <input type="radio" class="btn-check" name="format" value="ods" id="fmt-ods-${uid}" autocomplete="off">
        <label class="btn btn-outline-primary" for="fmt-ods-${uid}">ODS</label>
      </div>
      <hr class="my-2">
      <button type="submit" class="btn btn-primary btn-sm w-100">
        <i class="bi bi-download me-1"></i>${_("Export")}
      </button>
    </form>
  </div>
</div>
</%def>

<%def name="dropdown_order(items)">
<div class="btn-group">
  <div class="dropdown">
    <a class="btn btn-sm btn-secondary dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
      % if q["order"] == "asc":
        <i class="bi bi-caret-up-fill"></i>
      % else:
        <i class="bi bi-caret-down-fill"></i>
      % endif
      ${_("Order")}
    </a>
    <ul class="dropdown-menu">
      % for k, v in items.items():
      <li>
        <a class="dropdown-item" role="button" href="${request.current_route_url(_query={**q, 'order': k})}">
          % if k == q["order"]:
            <strong>${v}</strong>
          % else:
            ${v}
          % endif
        </a>
      </li>
      % endfor
    </ul>
  </div>
</div>
</%def>

<%def name="dropdown_filter(param, label, items)">
<div class="btn-group">
  <div class="dropdown">
    <a class="btn btn-sm btn-secondary dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
      % if q.get(param):
        <i class="bi bi-funnel-fill"></i>
      % else:
        <i class="bi bi-funnel"></i>
      % endif
      ${label}
    </a>
    <ul class="dropdown-menu">
      <li>
        <a class="dropdown-item" role="button" href="${request.current_route_url(_query={k: v for k, v in q.items() if k != param})}">
          % if not q.get(param):
            <strong>${_("All")}</strong>
          % else:
            ${_("All")}
          % endif
        </a>
      </li>
      % for k, v in items.items():
      <li>
        <a class="dropdown-item" role="button" href="${request.current_route_url(_query={**q, param: k})}">
          % if k == q.get(param):
            <strong>${v}</strong>
          % else:
            ${v}
          % endif
        </a>
      </li>
      % endfor
    </ul>
  </div>
</div>
</%def>