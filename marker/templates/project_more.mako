% for project in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
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
</tr>
% endfor