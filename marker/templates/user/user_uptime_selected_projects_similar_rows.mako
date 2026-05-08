<%
  per_page = 20
  offset = (page - 1) * per_page
%>
% for project in paginator:
% if loop.last and len(paginator) == per_page:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
  <td>${offset + loop.index + 1}</td>
  <td>${project.name}</td>
  <td class="text-break"><a href="${project.website if project.website.startswith(('http://', 'https://')) else 'https://' + project.website}" target="_blank" rel="noopener">${project.website}</a></td>
  <td hx-get="${request.route_url('project_uptime_check', _query={'url': project.website})}"
      hx-trigger="revealed"
      hx-swap="innerHTML">
    <div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div>
  </td>
</tr>
% endfor
