<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>Firma</th>
        <th class="col-2">Akcja</th>
      </tr>
    </thead>
    <tbody>
      % for company in project.companies:
      <tr>
        <td>
          % if company in request.identity.recomended:
          <i class="bi bi-hand-thumbs-up-fill"></i>
          % endif
          <a href="#top" hx-get="${request.route_url('company_view', company_id=company.id, slug=company.slug)}" hx-target="#main-container">${company.name}</a>
        </td>
        <td class="col-2"><button class="btn btn-secondary btn-sm" hx-post="${request.route_url('delete_project', company_id=company.id, project_id=project.id)}" hx-confirm="Czy jesteś pewny?" hx-target="closest tr" hx-swap="outerHTML swap:1s">Usuń</button></td>
      </tr>
      % endfor
    </tbody>
  </table>
</div>