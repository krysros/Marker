<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>
<%page args="tag, project"/>

% if tag:
<tr>
  <td>${checkbox.checkbox(tag, selected=request.identity.selected_tags, url=request.route_url('tag_check', tag_id=tag.id, slug=tag.slug))}</td>
  <td><a href="${request.route_url('tag_view', tag_id=tag.id, slug=tag.slug)}">${tag.name}</a></td>
  <td>${button.del_row(icon='dash-lg', color='warning', size='sm', url=request.route_url('unlink_tag_project', project_id=project.id, tag_id=tag.id))}</td>
</tr>
% endif