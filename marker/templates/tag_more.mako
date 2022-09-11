% for tag in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
  <td><a href="#" hx-get="${request.route_url('tag_view', tag_id=tag.id, slug=tag.slug)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">${tag.name}</a></td>
  <td>${tag.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>${tag.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
</tr>
% endfor