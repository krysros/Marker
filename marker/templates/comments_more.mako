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
    <a href="${request.route_url('company_view', company_id=comment.company.id, slug=comment.company.slug)}">${comment.company.name}</a>
    % if comment.created_by == request.identity or request.identity.name == 'admin':
    <span style="float:right;">
      <form hx-post="${request.route_url('comment_delete', comment_id=comment.id)}" hx-confirm="Czy jesteś pewny?" hx-target="closest .card" hx-swap="outerHTML swap:1s">
        <input type="hidden" name="csrf_token" value="${get_csrf_token()}">
        <button type="submit" class="btn btn-danger btn-sm">Usuń</button>
      </form>
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