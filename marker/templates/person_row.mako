<%namespace name="button" file="button.mako"/>

% if person:
<tr>
  <td><a href="${request.route_url('person_view', person_id=person.id, slug=person.slug)}">${person.name}</a></td>
  <td>${person.position}</td>
  <td>${person.phone}</td>
  <td><a href="mailto:${person.email}">${person.email}</a></td>
  <td class="col-2">
    <a class="btn btn-secondary btn-sm" href="${request.route_url('person_vcard', person_id=person.id, slug=person.slug)}">vCard</a>
    ${button.del_row('delete_person', person_id=person.id, slug=person.slug)}
  </td>
</tr>
% endif