<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>

% if tag:
<tr>
  <td class="col-1">${checkbox.tag(tag)}</td>
  <td><a href="${request.route_url('tag_view', tag_id=tag.id, slug=tag.slug)}">${tag.name}</a></td>
  <td class="col-2">${button.unlink('unlink_tag_from_company', company_id=company.id, tag_id=tag.id, size='sm')}</td>
</tr>
% endif