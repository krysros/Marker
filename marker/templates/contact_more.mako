% for contact in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
  <td><a href="${request.route_url('contact_view', contact_id=contact.id, slug=contact.slug)}">${contact.name}</a></td>
  % if contact.company:
  <td><a href="${request.route_url('company_view', company_id=contact.company.id, slug=contact.company.slug)}">${contact.company.name}</a></td>
  % elif contact.project:
  <td><a href="${request.route_url('project_view', project_id=contact.project.id, slug=contact.project.slug)}">${contact.project.name}</a></td>
  % else:
  <td>---</td>
  % endif
  % if contact.role:
  <td>${contact.role}</td>
  % else:
  <td>---</td>
  % endif
  % if contact.phone:
  <td>${contact.phone}</td>
  % else:
    <td>---</td>
  % endif
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