<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>

<%!
  def fmt_decimal(value):
      if value is None:
          return "---"
      formatted = f"{value:,.2f}"
      formatted = formatted.replace(",", "\u202f")
      return formatted
%>

<%def name="rows()">
<%
  show_shared_tags = bool(context.get("show_shared_tags", False))
  shared_tag_counts = context.get("shared_tag_counts", {})
  shared_tag_labels = context.get("shared_tag_labels", {})
  activity_values = context.get("activity_values")
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
    % if project.object_category:
    <small class="text-body-secondary">${_("Object category")}: ${project.object_category}</small><br>
    % endif
    ${_("Deadline")}: ${project.deadline or "---"}<br>
    <small class="text-body-secondary">${_("Created at")}: ${project.created_at.strftime('%Y-%m-%d %H:%M:%S')}</small><br>
    <small class="text-body-secondary">${_("Updated at")}: ${project.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</small>
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
  % if activity_values is not None:
  <%
    av = activity_values.get(project.id)
    vn = av.value_net if av else None
    vg = av.value_gross if av else None
    ua = project.usable_area
  %>
  <td class="text-end">${fmt_decimal(vn)}</td>
  <td class="text-end">${fmt_decimal(vg)}</td>
  <td class="text-end">${fmt_decimal(vn / ua) if vn is not None and ua else '---'}</td>
  <td class="text-end">${fmt_decimal(vg / ua) if vg is not None and ua else '---'}</td>
  % endif
  <td>
    <a href="${request.route_url('project_stars', project_id=project.id, slug=project.slug)}">
      <div hx-get="${request.route_url('project_count_stars', project_id=project.id, slug=project.slug)}"
           hx-trigger="starProjectEvent from:body"
           hx-target="#projects-stars-${project.id}"
           hx-swap="innerHTML">
        <span id="projects-stars-${project.id}" class="badge text-bg-secondary" role="button">${project.count_stars}</span>
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
</%def>

<%
  show_shared_tags = bool(context.get("show_shared_tags", False))
  activity_values = context.get("activity_values")
%>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>${checkbox.select_all()}</th>
        <th>${_("Project")}</th>
        <th>${_("City")}</th>
        % if show_shared_tags:
        <th>${_("Common tags")}</th>
        % endif
        <th>${_("Companies")}</th>
        % if activity_values is not None:
        <th class="text-end">${_("Value net")}</th>
        <th class="text-end">${_("Value gross")}</th>
        <th class="text-end">${_("Net / m2")}</th>
        <th class="text-end">${_("Gross / m2")}</th>
        % endif
        <th>${_("Stars")}</th>
        <th>${_("Comments")}</th>
        <th>${_("Action")}</th>
      </tr>
    </thead>
    <tbody>
      ${rows()}
    </tbody>
  </table>
</div>