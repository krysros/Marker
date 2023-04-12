<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th class="col-1">#</th>
        <th>${_("Company")}</th>
        <th>${_("Stage")}</th>
        <th>${_("Role")}</th>
        <th class="col-2">${_("Action")}</th>
      </tr>
    </thead>
    <tbody>
      % for assoc in project.companies:
      <tr>
        <td>${checkbox.checkbox(assoc.project, selected=request.identity.selected_projects, url=request.route_url('project_check', project_id=assoc.project.id, slug=assoc.project.slug))}</td>
        <td>
          <a href="${request.route_url('company_view', company_id=assoc.company.id, slug=assoc.company.slug)}">${assoc.company.name}</a>
        </td>
        <td>${stages.get(assoc.stage)}</td>
        <td>${company_roles.get(assoc.role)}</td>
        <td class="col-2">
          ${button.recommend(assoc.company, size='sm')}
          ${button.button(icon='dash-lg', color='warning', size='sm', url=request.route_url('unlink_company_project', company_id=assoc.company.id, project_id=assoc.project.id))}
        </td>
      </tr>
      % endfor
    </tbody>
  </table>
</div>