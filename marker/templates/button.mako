<%def name="show(route_name, size=None, **kwargs)">
<a class="btn btn-secondary${' btn-' + size if size else ''}" role="button" href="${request.route_url(route_name, **kwargs)}"><i class="bi bi-folder"></i></a>
</%def>

<%def name="search(route_name, size=None, **kwargs)">
<a class="btn btn-primary${' btn-' + size if size else ''}" role="button" href="${request.route_url(route_name, **kwargs)}"><i class="bi bi-search"></i></a>
</%def>

<%def name="export(route_name, size=None, **kwargs)">
<a class="btn btn-primary${' btn-' + size if size else ''}" role="button" href="${request.route_url(route_name, **kwargs)}"><i class="bi bi-download"></i></a>
</%def>

<%def name="table(route_name, size=None, **kwargs)">
<a class="btn btn-secondary${' btn-' + size if size else ''}" role="button" href="${request.route_url(route_name, **kwargs)}"><i class="bi bi-table"></i></a>
</%def>

<%def name="map(route_name, size=None, **kwargs)">
<a class="btn btn-secondary${' btn-' + size if size else ''}" role="button" href="${request.route_url(route_name, **kwargs)}"><i class="bi bi-map"></i></a>
</%def>

<%def name="vcard(route_name, size=None, **kwargs)">
<a class="btn btn-primary${' btn-' + size if size else ''}" role="button" href="${request.route_url(route_name, **kwargs)}"><i class="bi bi-person-vcard"></i></a>
</%def>

<%def name="add(route_name, size=None, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor' or 'admin':
<a class="btn btn-success${' btn-' + size if size else ''}" role="button" href="${request.route_url(route_name, **kwargs)}"><i class="bi bi-plus-lg"></i></a>
% else:
<button type="button" class="btn btn-success${' btn-' + size if size else ''}" disabled><i class="bi bi-plus-lg"></i></button>
% endif
</%def>

<%def name="edit(route_name, size=None, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor' or 'admin':
<a class="btn btn-warning${' btn-' + size if size else ''}" role="button" href="${request.route_url(route_name, **kwargs)}"><i class="bi bi-pencil-square"></i></a>
% else:
<button type="button" class="btn btn-warning${' btn-' + size if size else ''}" disabled><i class="bi bi-pencil-square"></i></button>
% endif
</%def>

<%def name="delete(route_name, size=None, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor' or 'admin':
<button type="button" class="btn btn-danger${' btn-' + size if size else ''}" hx-post="${request.route_url(route_name, **kwargs)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-confirm="Czy jesteś pewny?"><i class="bi bi-trash"></i></button>
% else:
<button type="button" class="btn btn-danger${' btn-' + size if size else ''}" disabled><i class="bi bi-trash"></i></button>
% endif
</%def>

<%def name="clear(route_name, icon, size=None, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor' or 'admin':
<button type="button" class="btn btn-danger${' btn-' + size if size else ''}" hx-post="${request.route_url(route_name, **kwargs)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-confirm="Czy jesteś pewny?"><i class="bi bi-${icon}"></i></button>
% else:
<button type="button" class="btn btn-danger${' btn-' + size if size else ''}" disabled><i class="bi bi-${icon}"></i></button>
% endif
</%def>

<%def name="unlink(route_name, size=None, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor' or 'admin':
<button type="button" class="btn btn-warning${' btn-' + size if size else ''}" hx-post="${request.route_url(route_name, **kwargs)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-confirm="Czy jesteś pewny?" hx-target="closest tr" hx-swap="outerHTML swap:1s"><i class="bi bi-dash-lg"></i></button>
% else:
<button type="button" class="btn btn-warning${' btn-' + size if size else ''}" disabled><i class="bi bi-dash-lg"></i></button>
% endif
</%def>

<%def name="del_card(route_name, size=None, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor' or 'admin':
<button type="button" class="btn btn-danger${' btn-' + size if size else ''}" hx-post="${request.route_url(route_name, **kwargs)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-confirm="Czy jesteś pewny?" hx-target="closest .card" hx-swap="outerHTML swap:1s"><i class="bi bi-trash"></i></button>
% else:
<button type="button" class="btn btn-danger${' btn-' + size if size else ''}" disabled><i class="bi bi-trash"></i></button>
% endif
</%def>

<%def name="del_row(route_name, size=None, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor' or 'admin':
<button type="button" class="btn btn-danger${' btn-' + size if size else ''}" hx-post="${request.route_url(route_name, **kwargs)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-confirm="Czy jesteś pewny?" hx-target="closest tr" hx-swap="outerHTML swap:1s"><i class="bi bi-trash"></i></button>
% else:
<button type="button" class="btn btn-danger${' btn-' + size if size else ''}" disabled><i class="bi bi-trash"></i></button>
% endif
</%def>

<%def name="recommend(company, size=None)">
<button class="btn btn-primary${' btn-' + size if size else ''}" hx-post="${request.route_url('company_recommend', company_id=company.id)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-target="#recommend-${company.id}" hx-swap="innerHTML">
  <div id="recommend-${company.id}">
  % if company in request.identity.recommended:
    <i class="bi bi-hand-thumbs-up-fill"></i>
  % else:
    <i class="bi bi-hand-thumbs-up"></i>
  % endif
  </div>
</button>
</%def>

<%def name="watch(project, size=None)">
<button class="btn btn-primary${' btn-' + size if size else ''}" hx-post="${request.route_url('project_watch', project_id=project.id)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-target="#watch-${project.id}" hx-swap="innerHTML">
  <div id="watch-${project.id}">
  % if project in request.identity.watched:
    <i class="bi bi-eye-fill"></i>
  % else:
    <i class="bi bi-eye"></i>
  % endif
  </div>
</button>
</%def>

<%def name="dropdown(route_name, dd_obj, **kwargs)">
<div class="btn-group">
  <div class="dropdown">
    <a class="btn btn-secondary dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
      ${dd_obj.icon | n} ${dd_obj.title}
    </a>
    <ul class="dropdown-menu">
      % for k, v in dd_obj.items.items():
        % if dd_obj.typ.name == "FILTER":
          <% query = {**search_query, 'filter': k, 'sort': dd_obj._sort, 'order': dd_obj._order} %>
        % elif dd_obj.typ.name == "SORT":
          <% query = {**search_query, 'filter': dd_obj._filter, 'sort': k, 'order': dd_obj._order} %>
        % elif dd_obj.typ.name == "ORDER":
          <% query = {**search_query, 'filter': dd_obj._filter, 'sort': dd_obj._sort, 'order': k} %>
        % endif
      <li>
        <a class="dropdown-item" role="button" href="${request.route_url(route_name, **kwargs, _query=query)}">
          % if k == dd_obj.current_item:
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