% if person:
<tr>
  <td><a href="#" hx-get="${request.route_url('person_view', person_id=person.id)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">${person.name}</a></td>
  <td>${person.position}</td>
  <td>${person.phone}</td>
  <td><a href="mailto:${person.email}">${person.email}</a></td>
  <td class="col-2">
    <a class="btn btn-secondary btn-sm" href="${request.route_url('person_vcard', person_id=person.id)}">vCard</a>
    <button class="btn btn-danger btn-sm" hx-post="${request.route_url('person_delete_from_company', person_id=person.id)}" hx-confirm="Czy jesteś pewny?" hx-target="closest tr" hx-swap="outerHTML swap:1s">Usuń</button>
  </td>
</tr>
% endif