<%
  per_page = 20
  offset = (page - 1) * per_page
%>
% for company in paginator:
% if loop.last and len(paginator) == per_page:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
  <td>${offset + loop.index + 1}</td>
  <td>${company.name}</td>
  <td class="text-break"><a href="${company.website if company.website.startswith(('http://', 'https://')) else 'https://' + company.website}" target="_blank" rel="noopener">${company.website}</a></td>
  <td hx-get="${request.route_url('company_uptime_check', _query={'url': company.website})}"
      hx-trigger="revealed"
      hx-swap="innerHTML">
    <div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div>
  </td>
</tr>
% endfor
