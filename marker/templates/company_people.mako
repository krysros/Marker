<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>Imię i nazwisko</th>
        <th>Stanowisko</th>
        <th>Telefon</th>
        <th>Email</th>
        <th class="col-2">Akcja</th>
      </tr>
    </thead>
    <tbody hx-confirm="Czy jesteś pewny" hx-target="closest tr" hx-swap="outerHTML swap:1s">
      % for person in company.people:
      <tr>
        <td>${person.name}</td>
        <td>${person.position}</td>
        <td>${person.phone}</td>
        <td><a href="mailto:${person.email}">${person.email}</a></td>
        <td class="col-2">
          <a class="btn btn-secondary btn-sm" href="${request.route_url('person_view', person_id=person.id)}">Pokaż</a> 
          <a class="btn btn-secondary btn-sm" href="${request.route_url('person_vcard', person_id=person.id)}">vCard</a>
          <button class="btn btn-danger btn-sm" hx-post="${request.route_url('person_delete_from_company', person_id=person.id)}">Usuń</button>
        </td>
      </tr>
      % endfor
    </tbody>
  </table>
</div>