<%namespace name="button" file="button.mako"/>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>Projekt</th>
        <th>Etap</th>
        <th>Rola</th>
        <th class="col-2">Akcja</th>
      </tr>
    </thead>
    <tbody>
      % for assoc in company.projects:
      <tr>
        <td>
          % if assoc.project in request.identity.watched:
            <i class="bi bi-eye-fill"></i>
          % endif
          <a href="${request.route_url('project_view', project_id=assoc.project.id, slug=assoc.project.slug)}">${assoc.project.name}</a>
        </td>
        <td>${stages.get(assoc.stage)}</td>
        <td>${company_roles.get(assoc.role)}</td>
        <td class="col-2">${button.unlink('unlink_project', company_id=assoc.company.id, project_id=assoc.project.id, size='sm')}</td>
      </tr>
      % endfor
    </tbody>
  </table>
</div>