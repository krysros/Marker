<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>

% for tag in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
  <td>${checkbox.checkbox(tag, selected=request.identity.selected_tags, url=request.route_url('tag_check', tag_id=tag.id, slug=tag.slug))}</td>
  <td>
    <a href="${request.route_url('tag_view', tag_id=tag.id, slug=tag.slug)}">${tag.name}</a><br>
    <small class="text-body-secondary">${_("Created at")}: ${tag.created_at.strftime('%Y-%m-%d %H:%M:%S')}</small><br>
    <small class="text-body-secondary">${_("Updated at")}: ${tag.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</small>
  </td>
  <td>
    <a href="${request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug)}">
      <span class="badge text-bg-secondary" role="button">${tag.count_companies}</span>
    </a>
  </td>
  <td>
    <a href="${request.route_url('tag_projects', tag_id=tag.id, slug=tag.slug)}">
      <span class="badge text-bg-secondary" role="button">${tag.count_projects}</span>
    </a>
  </td>
  <td>
    <div class="hstack gap-2 mx-2">
      ${button.a_button(icon='pencil-square', color='warning', size='sm', url=request.route_url('tag_edit', tag_id=tag.id, slug=tag.slug))}
      ${button.del_row(icon='trash', color='danger', size='sm', url=request.route_url('tag_del_row', tag_id=tag.id, slug=tag.slug))}
    </div>
  </td>
</tr>
% endfor