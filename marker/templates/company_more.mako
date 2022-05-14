% for company in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend"
    class="table-${company.category}">
% else:
<tr class="table-${company.category}">
% endif
  <td>
    % if company in request.identity.marker:
    <input type="checkbox"
           value="${company.id}"
           autocomplete="off"
           checked
           hx-post="${request.route_url('company_mark', company_id=company.id)}"
           hx-trigger="click"
           hx-swap="none">
    % else:
    <input type="checkbox"
           value="${company.id}"
           autocomplete="off"
           hx-post="${request.route_url('company_mark', company_id=company.id)}"
           hx-trigger="click"
           hx-swap="none">
    % endif
  </td>
  <td>
    % if company in request.identity.upvotes:
    <i class="fa fa-thumbs-up" aria-hidden="true"></i>
    % endif
    <a href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">${company.name}</a>
  </td>
  <td>${company.city}</td>
  <td>${voivodeships.get(company.voivodeship)}</td>
  <td>${company.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>${company.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td><a href="${request.route_url('company_upvotes', company_id=company.id, slug=company.slug)}">Pokaż</a> (${company.upvote_count})</td>
</tr>
% endfor