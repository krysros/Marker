<%inherit file="layout.mako"/>
<%namespace name="nav_pills" file="nav_pills.mako"/>
<%namespace name="modals" file="modals.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${nav_pills.project_pill(project)}</div>
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

<%include file="project_lead.mako"/>

<div id="relation">
  <%include file="company_list_projects.mako"/>
</div>

${modals.add_company_project(project)}
