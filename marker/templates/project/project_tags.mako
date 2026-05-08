<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <div class="me-auto">${pills.pills(project_pills)}</div>
% if request.identity.role == 'editor' or 'admin':
  <a href="${request.route_url('project_add_tag', project_id=project.id, slug=project.slug)}" class="btn btn-success"><i class="bi bi-plus-lg"></i></a>
% else:
  <button type="button" class="btn btn-success" disabled><i class="bi bi-plus-lg"></i></button>
% endif
</div>

<%include file="project_lead.mako"/>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
</div>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>${checkbox.select_all()}</th>
        <th>${_("Tag")}</th>
        <th>${_("Created at")}</th>
        <th>${_("Updated at")}</th>
        <th>${_("Action")}</th>
      </tr>
    </thead>
    <tbody id="new-tag">
      % for tag in tags:
        <%include file="tag_row_project.mako" args="tag=tag, project=project"/>
      % endfor
    </tbody>
  </table>
</div>