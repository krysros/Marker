<%inherit file="layout.mako"/>
<%namespace name="pills" file="company_pills.mako"/>
<%namespace name="modals" file="modals.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(company)}</div>
  <div>
    % if request.identity.role == 'editor' or 'admin':
    <button id="btn-add-comment" type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#modal-add-comment">
      <i class="bi bi-plus-lg"></i>
    </button>
    % else:
    <button type="button" class="btn btn-success" disabled><i class="bi bi-plus-lg"></i></button>
    % endif
  </div>
</div>

<%include file="company_lead.mako"/>

<div id="last-comment"></div>
<%include file="comment_more.mako"/>

${modals.add_comment(company)}