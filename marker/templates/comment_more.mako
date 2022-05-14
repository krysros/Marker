% for comment in paginator:
% if loop.last:
<div class="card"
  hx-get="${next_page}"
  hx-trigger="revealed"
  hx-swap="afterend">
% else:
<div class="card">
% endif
  <div class="card-header">
    <i class="fa fa-comment" aria-hidden="true"></i>
    <a href="${request.route_url('company_view', company_id=comment.company.id, slug=comment.company.slug)}">${comment.company.name}</a>
    % if comment.created_by == request.identity or request.identity.username == 'admin':
    <span style="float:right;"><a href="${request.route_url('comment_delete', comment_id=comment.id, _query={'from': 'company'})}">Usuń</a></span>
    % endif
  </div>
  <div class="card-body">
    <p>${comment.comment}</p>
  </div>
  <div class="card-footer">
    ${comment.created_at.strftime('%Y-%m-%d %H:%M:%S')} przez <a href="${request.route_url('user_view', username=comment.created_by.username, what='info')}" title="${comment.created_by.fullname}">${comment.created_by.username}</a>
  </div>
</div>
% endfor