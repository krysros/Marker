<%namespace name="button" file="button.mako"/>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th class="col-1">#</th>
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
          % if assoc.project in request.identity.selected_projects:
          <input class="form-check-input"
                type="checkbox"
                value="${assoc.project.id}"
                autocomplete="off"
                checked
                hx-post="${request.route_url('project_check', project_id=assoc.project.id)}"
                hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
                hx-trigger="click"
                hx-swap="none">
          % else:
          <input class="form-check-input"
                type="checkbox"
                value="${assoc.project.id}"
                autocomplete="off"
                hx-post="${request.route_url('project_check', project_id=assoc.project.id)}"
                hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
                hx-trigger="click"
                hx-swap="none">
          % endif
        </td>
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