% for person in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
  <td><a href="${request.route_url('person_view', person_id=person.id)}">${person.name}</a></td>
  % if person.company:
  <td><a href="${request.route_url('company_view', company_id=person.company.id, slug=person.company.slug)}">${person.company.name}</a></td>
  % else:
  <td>---</td>
  % endif
  <td>${person.position}</td>
  <td>${person.phone}</td>
  <td><a href="mailto:${person.email}">${person.email}</a></td>
  % if person.created_at:
  <td>${person.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  % else:
  <td>---</td>
  % endif
  % if person.updated_at:
  <td>${person.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  % else:
  <td>---</td>
  % endif
</tr>
% endfor