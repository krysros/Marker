<%namespace name="button" file="button.mako"/>

% if tag:
<tr>
  <td><a href="${request.route_url('tag_view', tag_id=tag.id, slug=tag.slug)}">${tag.name}</a></td>
  <td class="col-2">${button.unlink('unlink_tag', company_id=company.id, tag_id=tag.id, size='sm')}</td>
</tr>
% endif