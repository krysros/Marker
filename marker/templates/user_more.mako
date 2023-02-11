% for user in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
  <td><a href="${request.route_url('user_view', username=user.name)}">${user.name}</a></td>
  <td>${user.fullname or "---"}</td>
  <td>${user.email or "---"}</td>
  <td>${roles.get(user.role) or "---"}</td>
  <td>${user.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>${user.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
</tr>
% endfor