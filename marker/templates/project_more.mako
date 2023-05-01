<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>

<%!
  import pycountry
%>

% for project in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend"
    class="table-${project.color}">
% else:
<tr class="table-${project.color}">
% endif
  <td>${checkbox.checkbox(project, selected=request.identity.selected_projects, url=request.route_url('project_check', project_id=project.id, slug=project.slug))}</td>
  <td>
    <a href="${request.route_url('project_view', project_id=project.id, slug=project.slug)}">${project.name}</a><br>
    <small class="text-body-secondary">${_("Created at")}: ${project.created_at.strftime('%Y-%m-%d %H:%M:%S')}</small><br>
    <small class="text-body-secondary">${_("Updated at")}: ${project.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</small>
  </td>
  <td>${project.city or "---"}</td>
  <td>${getattr(pycountry.subdivisions.get(code=project.subdivision), "name", "---")}</td>
  <td>${getattr(pycountry.countries.get(alpha_2=project.country), "name", "---")}</td>
  <td>
    <a href="${request.route_url('project_watched', project_id=project.id, slug=project.slug)}">
      <div hx-get="${request.route_url('project_count_watched', project_id=project.id, slug=project.slug)}"
           hx-trigger="watchEvent from:body"
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
  <td>${project.deadline or "---"}</td>
  <td>
    <div class="hstack gap-2 mx-2">
      ${button.watch(project, size='sm')}
      ${button.a_button(icon='pencil-square', color='warning', size='sm', url=request.route_url('project_edit', project_id=project.id, slug=project.slug))}
      ${button.del_row(icon='trash', color='danger', size='sm', url=request.route_url('project_del_row', project_id=project.id, slug=project.slug))}
    </div>
  </td>
</tr>
% endfor