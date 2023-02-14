<%namespace name="button" file="button.mako"/>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th class="col-1">#</th>
        <th>Firma</th>
        <th>Etap</th>
        <th>Rola</th>
        <th class="col-2">Akcja</th>
      </tr>
    </thead>
    <tbody>
      % for assoc in project.companies:
      <tr>
        <td>
          % if assoc.company in request.identity.selected_companies:
          <input class="form-check-input"
                  type="checkbox"
                  value="${assoc.company.id}"
                  autocomplete="off"
                  checked
                  hx-post="${request.route_url('company_check', company_id=assoc.company.id)}"
                  hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
                  hx-trigger="click"
                  hx-swap="none">
          % else:
          <input class="form-check-input"
                  type="checkbox"
                  value="${assoc.company.id}"
                  autocomplete="off"
                  hx-post="${request.route_url('company_check', company_id=assoc.company.id)}"
                  hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
                  hx-trigger="click"
                  hx-swap="none">
          % endif
        </td>
        <td>
          % if assoc.company in request.identity.recommended:
          <i class="bi bi-hand-thumbs-up-fill"></i>
          % endif
          <a href="${request.route_url('company_view', company_id=assoc.company.id, slug=assoc.company.slug)}">${assoc.company.name}</a>
        </td>
        <td>${stages.get(assoc.stage)}</td>
        <td>${company_roles.get(assoc.role)}</td>
        <td class="col-2">${button.unlink('unlink_project', company_id=assoc.company.id, project_id=assoc.project.id, size='sm')}</td>
      </tr>
      % endfor
    </tbody>
  </table>
</div>