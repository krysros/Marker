% if comment:
<div class="card">
  <div class="card-header">
    <a href="#" hx-get="${request.route_url('company_view', company_id=comment.company.id, slug=comment.company.slug)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">${comment.company.name}</a>
    % if comment.created_by == request.identity or request.identity.name == 'admin':
    <span style="float:right;"><button class="btn btn-danger btn-sm" hx-post="${request.route_url('comment_delete', comment_id=comment.id)}" hx-confirm="Czy jesteś pewny?" hx-target="closest .card" hx-swap="outerHTML swap:1s">Usuń</button></span>
    % endif
  </div>
  <div class="card-body">
    <p>${comment.comment}</p>
  </div>
  <div class="card-footer">
    ${comment.created_at.strftime('%Y-%m-%d %H:%M:%S')} przez <a href="#" title="${comment.created_by.fullname}" hx-get="${request.route_url('user_view', username=comment.created_by.name, what='info')}" hx-target="#main-container" hx-swap="innerHTML show:window:top">${comment.created_by.name}</a>
  </div>
</div>
% endif