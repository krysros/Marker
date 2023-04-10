<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th class="col-1">#</th>
        <th>${_("Project")}</th>
        <th>${_("Stage")}</th>
        <th>${_("Role")}</th>
        <th class="col-2">${_("Action")}</th>
      </tr>
    </thead>
    <tbody>
      % for assoc in company.projects:
      <tr>
        <td>${checkbox.checkbox(assoc.project, selected=request.identity.selected_projects, url=request.route_url('project_check', project_id=assoc.project.id, slug=assoc.project.slug))}</td>
        <td>
          <a href="${request.route_url('project_view', project_id=assoc.project.id, slug=assoc.project.slug)}">${assoc.project.name}</a>
        </td>
        <td>${stages.get(assoc.stage)}</td>
        <td>${company_roles.get(assoc.role)}</td>
        <td class="col-2">
          ${button.watch(assoc.project, size='sm')}
          ${button.unlink('unlink_company_project', company_id=assoc.company.id, project_id=assoc.project.id, size='sm')}
        </td>
      </tr>
      % endfor
    </tbody>
  </table>
</div>