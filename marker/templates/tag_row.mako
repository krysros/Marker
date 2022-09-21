<%namespace name="button" file="button.mako"/>

% if tag:
<tr>
  <td><a href="#" hx-get="${request.route_url('tag_view', tag_id=tag.id, slug=tag.slug)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">${tag.name}</a></td>
  <td class="col-2">${button.del_row('delete_tag', company_id=company.id, tag_id=tag.id)}</td>
</tr>
% endif