% for project in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend"
    class="table-${project.color}">
% else:
<tr class="table-${project.color}">
% endif
  <td>
    % if project in request.identity.selected_projects:
    <input class="form-check-input"
          type="checkbox"
          value="${project.id}"
          autocomplete="off"
          checked
          hx-post="${request.route_url('project_check', project_id=project.id)}"
          hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
          hx-trigger="click"
          hx-swap="none">
    % else:
    <input class="form-check-input"
          type="checkbox"
          value="${project.id}"
          autocomplete="off"
          hx-post="${request.route_url('project_check', project_id=project.id)}"
          hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
          hx-trigger="click"
          hx-swap="none">
    % endif
  </td>
  <td>
  % if project in request.identity.watched:
    <i class="bi bi-eye-fill"></i>
  % endif
    <a href="${request.route_url('project_view', project_id=project.id, slug=project.slug)}">${project.name}</a>
  </td>
  <td>${project.city or "---"}</td>
  <td>${regions.get(project.region) or "---"}</td>
  <td>${project.deadline or "---"}</td>
  <td>${project.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>${project.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>
    % if project.count_watched > 0:
    <a href="${request.route_url('project_watched', project_id=project.id, slug=project.slug)}">
      <span class="badge text-bg-success" role="button">${project.count_watched}</span>
    </a>
    % else:
    <span class="badge text-bg-secondary">0</span>
    % endif
  </td>
  <td>
    % if project.count_comments > 0:
    <a href="${request.route_url('project_comments', project_id=project.id, slug=project.slug)}">
      <span class="badge text-bg-dark" role="button">${project.count_comments}</span>
    </a>
    % else:
    <span class="badge text-bg-secondary">0</span>
    % endif
  </td>
</tr>
% endfor