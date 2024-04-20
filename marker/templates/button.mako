<%def name="a_button(title=None, icon=None, color=None, size=None, url='#')">
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
    <a class="btn btn-secondary dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
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

<%def name="dropdown_order(items)">
<div class="btn-group">
  <div class="dropdown">
    <a class="btn btn-secondary dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
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