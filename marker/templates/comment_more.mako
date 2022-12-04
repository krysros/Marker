<%namespace name="button" file="button.mako"/>

% for comment in paginator:
% if loop.last:
<div class="card"
  hx-get="${next_page}"
  hx-trigger="revealed"
  hx-swap="afterend">
% else:
<div class="card mt-4 mb-4">
% endif
  <div class="card-header">
    <a href="${request.route_url('company_view', company_id=comment.company.id, slug=comment.company.slug)}">${comment.company.name}</a>
    % if comment.created_by == request.identity or request.identity.name == 'admin':
    <span style="float:right;">
      ${button.del_card('comment_delete', comment_id=comment.id, size='sm')}
    </span>
    % endif
  </div>
  <div class="card-body">
    <p>${comment.comment}</p>
  </div>
  <div class="card-footer">
    ${comment.created_at.strftime('%Y-%m-%d %H:%M:%S')} przez <a href="${request.route_url('user_view', username=comment.created_by.name)}" title="${comment.created_by.fullname}">${comment.created_by.name}</a>
  </div>
</div>
% endfor