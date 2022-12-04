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
  % if project in request.identity.watched:
    <i class="bi bi-eye-fill"></i>
  % endif
    <a href="${request.route_url('project_view', project_id=project.id, slug=project.slug)}">${project.name}</a>
  </td>
  <td>${project.deadline}</td>
  <td>${project.city}</td>
  <td>${states.get(project.state)}</td>
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
</tr>
% endfor