<%inherit file="layout.mako"/>
<%namespace name="pills" file="pills.mako"/>
<%namespace name="modals" file="modals.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(company_pills)}</div>
  <div>
    % if request.identity.role == 'editor' or 'admin':
    <button id="btn-add-relation" type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#modal-add-relation">
      <i class="bi bi-plus-lg"></i>
    </button>
    % else:
    <button type="button" class="btn btn-success" disabled><i class="bi bi-plus-lg"></i></button>
    % endif
  </div>
</div>

<%include file="company_lead.mako"/>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th class="col-1">#</th>
        <th>${_("Project")}</th>
        <th>${_("Stage")}</th>
        <th>${_("Role")}</th>
        <th class="col-2">${_("Action")}</th>
      </tr>
    </thead>
    <tbody id="new-assoc">
      % for assoc in company.projects:
        <%include file="project_row_assoc.mako" args="assoc=assoc"/>
      % endfor
    </tbody>
  </table>
</div>

${modals.add_company_project(company)}