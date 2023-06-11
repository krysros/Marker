<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>
<%page args="assoc"/>

% if assoc:
<tr>
  <td>${checkbox.checkbox(assoc.project, selected=request.identity.selected_projects, url=request.route_url('project_check', project_id=assoc.project.id, slug=assoc.project.slug))}</td>
  <td>
    <a href="${request.route_url('project_view', project_id=assoc.project.id, slug=assoc.project.slug)}">${assoc.project.name}</a>
  </td>
  <td>${stages.get(assoc.stage)}</td>
  <td>${company_roles.get(assoc.role)}</td>
  <td>
    <div class="hstack gap-2 mx-2">
      ${button.project_star(assoc.project, size='sm')}
      ${button.del_row(icon='dash-lg', color='warning', size='sm', url=request.route_url('unlink_company_project', company_id=assoc.company.id, project_id=assoc.project.id))}
    </div>
  </td>
</tr>
% endif