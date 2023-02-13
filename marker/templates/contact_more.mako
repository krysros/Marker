% for contact in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
  <td>
    % if contact in request.identity.selected_contacts:
    <input class="form-check-input"
          type="checkbox"
          value="${contact.id}"
          autocomplete="off"
          checked
          hx-post="${request.route_url('contact_check', contact_id=contact.id)}"
          hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
          hx-trigger="click"
          hx-swap="none">
    % else:
    <input class="form-check-input"
          type="checkbox"
          value="${contact.id}"
          autocomplete="off"
          hx-post="${request.route_url('contact_check', contact_id=contact.id)}"
          hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
          hx-trigger="click"
          hx-swap="none">
    % endif
  </td>
  <td><a href="${request.route_url('contact_view', contact_id=contact.id, slug=contact.slug)}">${contact.name}</a></td>
  % if contact.company:
  <td><a href="${request.route_url('company_view', company_id=contact.company.id, slug=contact.company.slug)}">${contact.company.name}</a></td>
  % elif contact.project:
  <td><a href="${request.route_url('project_view', project_id=contact.project.id, slug=contact.project.slug)}">${contact.project.name}</a></td>
  % else:
  <td>---</td>
  % endif
  <td>${contact.role or "---"}</td>
  <td>${contact.phone or "---"}</td>
  % if contact.email:
  <td><a href="mailto:${contact.email}">${contact.email}</a></td>
  % else:
  <td>---</td>
  % endif
  % if contact.created_at:
  <td>${contact.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  % else:
  <td>---</td>
  % endif
  % if contact.updated_at:
  <td>${contact.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  % else:
  <td>---</td>
  % endif
</tr>
% endfor