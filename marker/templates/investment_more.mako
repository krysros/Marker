% for investment in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
  <td>
    % if investment in request.identity.following:
    <i class="fa fa-eye" aria-hidden="true"></i>
    % endif
    <a href="${request.route_url('investment_view', investment_id=investment.id, slug=investment.slug)}">${investment.name}</a>
  </td>
  <td>${investment.city}</td>
  <td>${investment.deadline}</td>
  <td>${investment.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>${investment.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
</tr>
% endfor