<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>

% for project in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend"
    class="table-${project.color}">
% else:
<tr class="table-${project.color}">
% endif
  <td>${checkbox.project(project)}</td>
  <td>
    <a href="${request.route_url('project_view', project_id=project.id, slug=project.slug)}">${project.name}</a>
  </td>
  <td>${project.city or "---"}</td>
  <td>${regions.get(project.region) or "---"}</td>
  <td>${project.deadline or "---"}</td>
  <td>${project.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>${project.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>
    <a href="${request.route_url('project_watched', project_id=project.id, slug=project.slug)}">
      <div hx-get="${request.route_url('count_project_watched', project_id=project.id, slug=project.slug)}"
            hx-trigger="watchedProjectEvent from:body"
            hx-target="#watched-${project.id}"
            hx-swap="innerHTML">
        <span id="watched-${project.id}" class="badge text-bg-secondary" role="button">${project.count_watched}</swap>
      </div>
    </a>
  </td>
  <td>
    <a href="${request.route_url('project_comments', project_id=project.id, slug=project.slug)}">
      <span class="badge text-bg-secondary" role="button">${project.count_comments}</span>
    </a>
  </td>
  <td>
    ${button.watch(project, size='sm')}
    ${button.edit('project_edit', project_id=project.id, slug=project.slug, size='sm')}
    ${button.del_row('delete_project', project_id=project.id, slug=project.slug, size='sm')}
  </td>
</tr>
% endfor