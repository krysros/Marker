<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>

% if contact:
<tr>
  <td>${checkbox.contact(contact)}</td>
  <td><a href="${request.route_url('contact_view', contact_id=contact.id, slug=contact.slug)}">${contact.name}</a></td>
  <td>${contact.role}</td>
  <td>${contact.phone}</td>
  <td><a href="mailto:${contact.email}">${contact.email}</a></td>
  <td class="col-2">
    ${button.vcard('contact_vcard', contact_id=contact.id, slug=contact.slug, size='sm')}
    ${button.del_row('delete_contact', contact_id=contact.id, slug=contact.slug, size='sm')}
  </td>
</tr>
% endif