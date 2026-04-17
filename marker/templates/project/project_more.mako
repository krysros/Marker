<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>

<%
  show_shared_tags = bool(context.get("show_shared_tags", False))
  shared_tag_counts = context.get("shared_tag_counts", {})
  shared_tag_labels = context.get("shared_tag_labels", {})
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
  <td>${checkbox.checkbox(project, selected_ids=selected_ids('selected_projects'), url=request.route_url('project_check', project_id=project.id, slug=project.slug))}</td>
  <td>
    <a href="${request.route_url('project_view', project_id=project.id, slug=project.slug)}">${project.name}</a><br>
    ${_("Deadline")}: ${project.deadline or "---"}<br>
    <small class="text-body-secondary">${_("Created at")}: ${project.created_at.strftime('%Y-%m-%d %H:%M:%S')}</small><br>
    <small class="text-body-secondary">${_("Updated at")}: ${project.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</small>
  </td>
  <td>
    % if project.object_category:
      ${project.object_category}
    % else:
      ---
    % endif
  </td>
  <td>
    ${project.city or "---"}<br>
    <small class="text-body-secondary">${get_subdivision_name(project.subdivision, "---")}</small><br>
    <small class="text-body-secondary">${get_country_name(project.country, "---")}</small>
  </td>
  % if show_shared_tags:
  <td>
    <span class="badge text-bg-info"
          role="button"
          tabindex="0"
          data-bs-toggle="popover"
          data-bs-trigger="hover focus"
          data-bs-placement="top"
          data-bs-title="${_("Common tags")}" 
          data-bs-content="${shared_tag_labels.get(project.id, '')}">
      ${shared_tag_counts.get(project.id, 0)}
    </span>
  </td>
  % endif
  <td>
    <a href="${request.route_url('project_companies', project_id=project.id, slug=project.slug)}">
      <span class="badge text-bg-secondary" role="button">${project.count_companies}</span>
    </a>
  </td>
  <td>
    <a href="${request.route_url('project_stars', project_id=project.id, slug=project.slug)}"
      <div hx-get="${request.route_url('project_count_stars', project_id=project.id, slug=project.slug)}"
           hx-trigger="starProjectEvent from:body"
           hx-target="#projects-stars-${project.id}"
           hx-swap="innerHTML">
        <span id="projects-stars-${project.id}" class="badge text-bg-secondary" role="button">${project.count_stars}</swap>
      </div>
    </a>
  </td>
  <td>
    <a href="${request.route_url('project_comments', project_id=project.id, slug=project.slug)}">
      <span class="badge text-bg-secondary" role="button">${project.count_comments}</span>
    </a>
  </td>
  <td>
    <div class="hstack gap-2 mx-2">
      ${button.project_star(project, size='sm')}
      ${button.a(icon='pencil-square', color='warning', size='sm', url=request.route_url('project_edit', project_id=project.id, slug=project.slug))}
      ${button.del_row(icon='trash', color='danger', size='sm', url=request.route_url('project_del_row', project_id=project.id, slug=project.slug))}
    </div>
  </td>
</tr>
% endfor