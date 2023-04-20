<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>
<%namespace name="modals" file="modals.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(project_pills)}</div>
  <div>
    % if request.identity.role == 'editor' or 'admin':
    <button id="btn-add-tag" type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#modal-add-tag">
      <i class="bi bi-plus-lg"></i>
    </button>
    % else:
    <button type="button" class="btn btn-success" disabled><i class="bi bi-plus-lg"></i></button>
    % endif
  </div>
</div>

<%include file="project_lead.mako"/>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th class="col-1">#</th>
        <th>${_("Tag")}</th>
        <th class="col-2">${_("Action")}</th>
      </tr>
    </thead>
    <tbody id="new-tag">
      % for tag in project.tags:
        <%include file="tag_row_project.mako" args="tag=tag, project=project"/>
      % endfor
    </tbody>
  </table>
</div>

${modals.add_tag(project)}
