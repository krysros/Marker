% for user in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
  <td><a href="#top" hx-get="${request.route_url('user_view', username=user.name)}" hx-target="#main-container" hx-swap="innerHTML">${user.name}</a></td>
  <td>${user.fullname}</td>
  <td>${user.email}</td>
  <td>${user.role}</td>
  <td>${user.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>${user.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
</tr>
% endfor