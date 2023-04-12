<%! import markdown %>
<%page args="comment"/>
<%namespace name="button" file="button.mako"/>

<div class="card mt-4 mb-4">
  <div class="card-header">
    % if comment.company:
    <span class="badge bg-secondary">${_("Company")}</span>&nbsp;
    <a href="${request.route_url('company_view', company_id=comment.company.id, slug=comment.company.slug)}">${comment.company.name}</a>
    % elif comment.project:
    <span class="badge bg-secondary">${_("Project")}</span>&nbsp;
    <a href="${request.route_url('project_view', project_id=comment.project.id, slug=comment.project.slug)}">${comment.project.name}</a>
    % endif
    % if comment.created_by == request.identity or request.identity.name == 'admin':
    <span style="float:right;">
      ${button.del_card(icon='trash', color='danger', size='sm', url=request.route_url('comment_delete', comment_id=comment.id))}
    </span>
    % endif
  </div>
  <div class="card-body">
    ${markdown.markdown(comment.comment) | n}
  </div>
  <div class="card-footer">
    ${comment.created_at.strftime('%Y-%m-%d %H:%M:%S')} ${_("by")} <a href="${request.route_url('user_view', username=comment.created_by.name)}" title="${comment.created_by.fullname}">${comment.created_by.name}</a>
  </div>
</div>