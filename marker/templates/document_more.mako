% for document in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
  <td>${document.filename}</td>
  <td>${doctypes.get(document.typ)}</td>
  <td>${document.added.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td><a href="${request.route_url('user_view', username=document.added_by.username, what='info')}">${document.added_by.username}</a></td>
  <td>
    <form method="post">
      <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
      <button type="submit" class="btn btn-primary btn-sm" formaction="${request.route_url('document_download', document_id=document.id)}"><i class="fa fa-download" aria-hidden="true"></i></button>
      <button type="submit" class="btn btn-danger btn-sm" formaction="${request.route_url('document_delete', document_id=document.id)}"><i class="fa fa-times" aria-hidden="true"></i></button>
    </form>
  </td>
</tr>
% endfor