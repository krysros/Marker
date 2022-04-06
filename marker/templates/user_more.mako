% for user in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
  <td><a href="${request.route_url('user_view', username=user.username)}">${user.username}</a></td>
  <td>${user.fullname}</td>
  <td>${user.email}</td>
  <td>${user.role}</td>
  <td>${user.added.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>${user.edited.strftime('%Y-%m-%d %H:%M:%S')}</td>
</tr>
% endfor