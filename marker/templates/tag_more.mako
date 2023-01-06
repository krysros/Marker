% for tag in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
  <td><a href="${request.route_url('tag_view', tag_id=tag.id, slug=tag.slug)}">${tag.name}</a></td>
  <td>${tag.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>${tag.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>
    % if tag.count_companies > 0:
    <a href="${request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug)}">
      <span class="badge text-bg-success" role="button">${tag.count_companies}</span>
    </a>
    % else:
    <span class="badge text-bg-secondary">0</span>
    % endif
  </td>
  <td>
    % if tag.count_projects > 0:
    <a href="${request.route_url('tag_projects', tag_id=tag.id, slug=tag.slug)}">
      <span class="badge text-bg-success" role="button">${tag.count_projects}</span>
    </a>
    % else:
    <span class="badge text-bg-secondary">0</span>
    % endif
  </td>
</tr>
% endfor