% for person in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend">
% else:
<tr>
% endif
  <td>${person.name}</td>
  % if person.company:
  <td><a href="${request.route_url('company_view', company_id=person.company.id, slug=person.company.slug)}">${person.company.name}</a></td>
  % else:
  <td>---</td>
  % endif
  <td>${person.phone}</td>
  <td><a href="mailto:${person.email}">${person.email}</a></td>
</tr>
% endfor