% if comment:
<div class="card">
  <div class="card-header">
    <a href="${request.route_url('company_view', company_id=comment.company.id, slug=comment.company.slug)}">${comment.company.name}</a>
    % if comment.created_by == request.identity or request.identity.name == 'admin':
    <span style="float:right;"><a href="${request.route_url('comment_delete', comment_id=comment.id, _query={'from': 'company'})}">Usuń</a></span>
    % endif
  </div>
  <div class="card-body">
    <p>${comment.comment}</p>
  </div>
  <div class="card-footer">
    ${comment.created_at.strftime('%Y-%m-%d %H:%M:%S')} przez <a href="${request.route_url('user_view', username=comment.created_by.name, what='info')}" title="${comment.created_by.fullname}">${comment.created_by.name}</a>
  </div>
</div>
% endif