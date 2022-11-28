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
          % if company in request.identity.recommended:
          <i class="bi bi-hand-thumbs-up-fill"></i>
          % endif
          <a href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">${company.name}</a>
        </td>
        <td class="col-2">${button.unlink('unlink_project', company_id=company.id, project_id=project.id)}</td>
      </tr>
      % endfor
    </tbody>
  </table>
</div>