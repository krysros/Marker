<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>
<%page args="assoc"/>

% if assoc:
<tr>
  <td>${checkbox.checkbox(assoc.company, selected_ids=selected_ids('selected_companies'), url=request.route_url('company_check', company_id=assoc.company.id, slug=assoc.company.slug))}</td>
  <td>
    <a href="${request.route_url('company_view', company_id=assoc.company.id, slug=assoc.company.slug)}">${assoc.company.name}</a>
  </td>
  <td>${stages.get(assoc.stage)}</td>
  <td>${company_roles.get(assoc.role)}</td>
  <td>${assoc.company.created_at.strftime('%Y-%m-%d %H:%M:%S') if assoc.company.created_at else '---'}</td>
  <td>${assoc.company.updated_at.strftime('%Y-%m-%d %H:%M:%S') if assoc.company.updated_at else '---'}</td>
  <td>
    <div class="hstack gap-2 mx-2">
      ${button.company_star(assoc.company, size='sm')}
      ${button.a(icon='pencil-square', color='warning', size='sm', url=request.route_url('company_activity_edit', company_id=assoc.company.id, project_id=assoc.project.id))}
      ${button.del_row(icon='dash-lg', color='danger', size='sm', url=request.route_url('activity_unlink', company_id=assoc.company.id, project_id=assoc.project.id))}
    </div>
  </td>
</tr>
% endif