<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>

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
        <td>${checkbox.project(assoc.project)}</td>
        <td>
          <a href="${request.route_url('company_view', company_id=assoc.company.id, slug=assoc.company.slug)}">${assoc.company.name}</a>
        </td>
        <td>${stages.get(assoc.stage)}</td>
        <td>${company_roles.get(assoc.role)}</td>
        <td class="col-2">
          ${button.recommend(assoc.company, size='sm')}
          ${button.unlink('unlink_company_project', company_id=assoc.company.id, project_id=assoc.project.id, size='sm')}
        </td>
      </tr>
      % endfor
    </tbody>
  </table>
</div>