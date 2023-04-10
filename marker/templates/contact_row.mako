<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>
<%page args="contact"/>

% if contact:
<tr>
  <td>${checkbox.checkbox(contact, selected=request.identity.selected_contacts, url=request.route_url('contact_check', contact_id=contact.id, slug=contact.slug))}</td>
  <td><a href="${request.route_url('contact_view', contact_id=contact.id, slug=contact.slug)}">${contact.name or "---"}</a></td>
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
  <td class="col-2">
    ${button.vcard('contact_vcard', contact_id=contact.id, slug=contact.slug, size='sm')}
    ${button.edit('contact_edit', contact_id=contact.id, slug=contact.slug, size='sm')}
    ${button.del_row('contact_del_row', contact_id=contact.id, slug=contact.slug, size='sm')}
  </td>
</tr>
% endif