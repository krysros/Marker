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
          <a href="#" hx-get="${request.route_url('project_view', project_id=project.id, slug=project.slug)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">${project.name}</a>
        </td>
        <td class="col-2"><button class="btn btn-secondary btn-sm" hx-post="${request.route_url('delete_project', company_id=company.id, project_id=project.id)}" hx-confirm="Czy jesteś pewny?" hx-target="closest tr" hx-swap="outerHTML swap:1s">Usuń</button></td>
      </tr>
      % endfor
    </tbody>
  </table>
</div>