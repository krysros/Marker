% for tender in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
  <td>
    % if tender in request.identity.following:
    <i class="fa fa-eye" aria-hidden="true"></i>
    % endif
    <a href="${request.route_url('tender_view', tender_id=tender.id, slug=tender.slug)}">${tender.name}</a>
  </td>
  <td>${tender.city}</td>
  <td>${tender.deadline}</td>
  <td>${tender.added.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>${tender.edited.strftime('%Y-%m-%d %H:%M:%S')}</td>
</tr>
% endfor