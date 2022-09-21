<%namespace name="button" file="button.mako"/>

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
          <a href="#" hx-get="${request.route_url('company_view', company_id=company.id, slug=company.slug)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">${company.name}</a>
        </td>
        <td class="col-2">${button.del_row('delete_project', company_id=company.id, project_id=project.id)}</td>
      </tr>
      % endfor
    </tbody>
  </table>
</div>