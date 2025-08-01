<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>
<%page args="assoc"/>

% if assoc:
<tr>
  <td>${checkbox.checkbox(assoc.project, selected=request.identity.selected_projects, url=request.route_url('project_check', project_id=assoc.project.id, slug=assoc.project.slug))}</td>
  <td>
    <a href="${request.route_url('company_view', company_id=assoc.company.id, slug=assoc.company.slug)}">${assoc.company.name}</a>
  </td>
  <td>${stages.get(assoc.stage)}</td>
  <td>${company_roles.get(assoc.role)}</td>
  <td>
    <div class="hstack gap-2 mx-2">
      ${button.company_star(assoc.company, size='sm')}
      ${button.a(icon='pencil-square', color='warning', size='sm', url=request.route_url('company_activity_edit', company_id=assoc.company.id, project_id=assoc.project.id))}
      ${button.del_row(icon='dash-lg', color='danger', size='sm', url=request.route_url('activity_unlink', company_id=assoc.company.id, project_id=assoc.project.id))}
    </div>
  </td>
</tr>
% endif