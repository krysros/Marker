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
</%def>

<%def name="recommend(company, size=None)">
<button class="btn btn-primary${' btn-' + size if size else ''}" hx-post="${request.route_url('company_recommend', company_id=company.id, slug=company.slug)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-target="#recommend-${company.id}" hx-swap="innerHTML">
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
<button class="btn btn-primary${' btn-' + size if size else ''}" hx-post="${request.route_url('project_watch', project_id=project.id, slug=project.slug)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-target="#watch-${project.id}" hx-swap="innerHTML">
  <div id="watch-${project.id}">
  % if project in request.identity.watched:
    <i class="bi bi-eye-fill"></i>
  % else:
    <i class="bi bi-eye"></i>
  % endif
  </div>
</button>
</%def>

<%def name="dropdown(dd)">
<div class="btn-group">
  <div class="dropdown">
    <a class="btn btn-secondary dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
      ${dd.icon | n} ${dd.title}
    </a>
    <ul class="dropdown-menu">
      % for k, v in dd.items.items():
        % if dd.typ.name == "FILTER":
          <% query = {**dd.q, 'filter': k, 'sort': dd._sort, 'order': dd._order} %>
        % elif dd.typ.name == "SORT":
          <% query = {**dd.q, 'filter': dd._filter, 'sort': k, 'order': dd._order} %>
        % elif dd.typ.name == "ORDER":
          <% query = {**dd.q, 'filter': dd._filter, 'sort': dd._sort, 'order': k} %>
        % endif
      <li>
        <a class="dropdown-item" role="button" href="${request.current_route_url(_query=query)}">
          % if k == dd.current_item:
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