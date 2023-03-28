<%inherit file="layout.mako"/>
<%namespace name="pills" file="pills.mako"/>
<%namespace name="modals" file="modals.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.company_pill(company)}</div>
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

<div id="relation">
  <%include file="project_list_companies.mako"/>
</div>

${modals.add_company_project(company)}