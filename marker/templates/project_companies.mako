<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>Firma</th>
        <th class="col-2">Akcja</th>
      </tr>
    </thead>
    <tbody hx-confirm="Czy jesteś pewny?" hx-target="closest tr" hx-swap="outerHTML swap:1s">
      % for company in project.companies:
      <tr>
        <td><a href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">${company.name}</a></td>
        <td class="col-2"><button class="btn btn-secondary btn-sm" hx-post="${request.route_url('delete_company_from_project', project_id=project.id, company_id=company.id)}">Usuń</button></td>
      </tr>
      % endfor
    </tbody>
  </table>
</div>