<%namespace name="button" file="button.mako"/>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>Projekt</th>
        <th class="col-2">Akcja</th>
      </tr>
    </thead>
    <tbody>
      % for project in company.projects:
      <tr>
        <td>
          % if project in request.identity.watched:
            <i class="bi bi-eye-fill"></i>
          % endif
          <a href="${request.route_url('project_view', project_id=project.id, slug=project.slug)}">${project.name}</a>
        </td>
        <td class="col-2">${button.unlink('unlink_project', company_id=company.id, project_id=project.id, size='sm')}</td>
      </tr>
      % endfor
    </tbody>
  </table>
</div>