<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>
<%page args="contact"/>

% if contact:
<tr>
  <td>${checkbox.checkbox(contact, selected=request.identity.selected_contacts, url=request.route_url('contact_check', contact_id=contact.id, slug=contact.slug))}</td>
  <td>
    <a href="${request.route_url('contact_view', contact_id=contact.id, slug=contact.slug)}">${contact.name or "---"}</a><br>
    <small class="text-body-secondary">${_("Created at")}: ${contact.created_at.strftime('%Y-%m-%d %H:%M:%S')}</small><br>
    <small class="text-body-secondary">${_("Updated at")}: ${contact.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</small>
  </td>
  <td>${contact.role or "---"}</td>
  <td>${contact.phone or "---"}</td>
  % if contact.email:
  <td><a href="mailto:${contact.email}">${contact.email}</a></td>
  % else:
  <td>---</td>
  % endif
  <td>
    <div class="hstack gap-2 mx-2">
      ${button.a(icon='person-vcard', color='primary', size='sm', url=request.route_url('contact_vcard', contact_id=contact.id, slug=contact.slug))}
      ${button.a(icon='pencil-square', color='warning', size='sm', url=request.route_url('contact_edit', contact_id=contact.id, slug=contact.slug))}
      ${button.del_row(icon='trash', color='danger', size='sm', url=request.route_url('contact_del_row', contact_id=contact.id, slug=contact.slug))}
    </div>
  </td>
</tr>
% endif