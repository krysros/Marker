<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-diagram-3"></i> ${_("Contractors")}
  <span class="badge bg-secondary">${counter}</span>
</h2>

<hr>

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

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div class="dropdown">
    <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
      % if q.get('role', []):
        <i class="bi bi-person-fill"></i>
      % else:
        <i class="bi bi-person"></i>
      % endif
      ${_("Role")}
    </button>
    <form class="dropdown-menu p-3" style="min-width: 260px;" method="get">
      ${preserve_params({'role'})}
      <div class="mb-3">
        <label for="contractor-filter-roles" class="form-label">${_("Role")}</label>
        <select id="contractor-filter-roles" class="form-control" name="role" multiple size="8">
          % for role_key, role_label in available_roles:
          <option value="${role_key}" ${'selected' if role_key in q.get('role', []) else ''}>${role_label}</option>
          % endfor
        </select>
        <small class="text-body-secondary">Ctrl + Click</small>
      </div>
      <div class="hstack gap-2">
        <button type="submit" class="btn btn-primary btn-sm">${_("Submit")}</button>
        <% clear_q = {k: v for k, v in q.items() if k != 'role'} %>
        <a class="btn btn-outline-secondary btn-sm" href="${request.current_route_url(_query=clear_q)}">${_("Clear")}</a>
      </div>
    </form>
  </div>
  <div class="dropdown">
    <button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
      % if q.get('tag', []):
        <i class="bi bi-tags-fill"></i>
      % else:
        <i class="bi bi-tags"></i>
      % endif
      ${_("Tags")}
    </button>
    <form class="dropdown-menu p-3" style="min-width: 260px;" method="get">
      ${preserve_params({'tag'})}
      <div class="mb-3">
        <label for="contractor-filter-tags" class="form-label">${_("Tags")}</label>
        <select id="contractor-filter-tags" class="form-control" name="tag" multiple size="10">
          % for tag_name in available_tags:
          <option value="${tag_name}" ${'selected' if tag_name in q.get('tag', []) else ''}>${tag_name}</option>
          % endfor
        </select>
        <small class="text-body-secondary">Ctrl + Click</small>
      </div>
      <div class="hstack gap-2">
        <button type="submit" class="btn btn-primary btn-sm">${_("Submit")}</button>
        <% clear_q = {k: v for k, v in q.items() if k != 'tag'} %>
        <a class="btn btn-outline-secondary btn-sm" href="${request.current_route_url(_query=clear_q)}">${_("Clear")}</a>
      </div>
    </form>
  </div>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="company_table.mako"/>