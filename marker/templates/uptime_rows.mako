<%def name="rows(items, page, next_page, check_route_name)">
<%
  per_page = 20
  offset = (page - 1) * per_page
%>
% for item in items:
% if loop.last and len(items) == per_page:
<tr hx-get="${next_page}"
    hx-trigger="intersect once"
    hx-swap="afterend">
% else:
<tr>
% endif
  <td>${offset + loop.index + 1}</td>
  <td>${item.name}</td>
  <td class="text-break"><a href="${external_url(item.website)}" target="_blank" rel="noopener">${item.website}</a></td>
  <td hx-get="${request.route_url(check_route_name, _query={'url': item.website})}"
      hx-trigger="intersect once"
      hx-swap="innerHTML">
    <div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div>
  </td>
</tr>
% endfor
</%def>