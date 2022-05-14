% for branch in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
  <td><a href="${request.route_url('branch_view', branch_id=branch.id, slug=branch.slug)}">${branch.name}</a></td>
  <td>${branch.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>${branch.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
</tr>
% endfor