% if comment:
<div class="card">
  <div class="card-header">
    <a href="#top" hx-get="${request.route_url('company_view', company_id=comment.company.id, slug=comment.company.slug)}" hx-target="#main-container" hx-swap="innerHTML">${comment.company.name}</a>
    % if comment.created_by == request.identity or request.identity.name == 'admin':
    <span style="float:right;"><a class="btn btn-danger btn-sm" role="button" hx-get="${request.route_url('comment_delete', comment_id=comment.id, _query={'from': 'company'})}" hx-target="#main-container" hx-swap="innerHTML">Usuń</a></span>
    % endif
  </div>
  <div class="card-body">
    <p>${comment.comment}</p>
  </div>
  <div class="card-footer">
    ${comment.created_at.strftime('%Y-%m-%d %H:%M:%S')} przez <a href="#top" title="${comment.created_by.fullname}" hx-get="${request.route_url('user_view', username=comment.created_by.name, what='info')}" hx-target="#main-container" hx-swap="innerHTML">${comment.created_by.name}</a>
  </div>
</div>
% endif