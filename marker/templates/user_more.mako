% for user in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
  <td>
    <a href="${request.route_url('user_view', username=user.name)}">${user.name}</a><br>
    ${_("Role")}: ${roles.get(user.role) or "---"}<br>
    <small class="text-body-secondary">${_("Created at")}: ${user.created_at.strftime('%Y-%m-%d %H:%M:%S')}</small><br>
    <small class="text-body-secondary">${_("Updated at")}: ${user.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</small>
  </td>
  <td>${user.fullname or "---"}</td>
  <td>${user.email or "---"}</td>
</tr>
% endfor