% for company in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend"
    class="table-${company.color}">
% else:
<tr class="table-${company.color}">
% endif
  <td>
    % if company in request.identity.checked:
    <input class="form-check-input"
           type="checkbox"
           value="${company.id}"
           autocomplete="off"
           checked
           hx-post="${request.route_url('company_check', company_id=company.id)}"
           hx-trigger="click"
           hx-swap="none">
    % else:
    <input class="form-check-input"
           type="checkbox"
           value="${company.id}"
           autocomplete="off"
           hx-post="${request.route_url('company_check', company_id=company.id)}"
           hx-trigger="click"
           hx-swap="none">
    % endif
  </td>
  <td>
    % if company in request.identity.recomended:
    <i class="bi bi-hand-thumbs-up-fill"></i>
    % endif
    <a href="#top" hx-get="${request.route_url('company_view', company_id=company.id, slug=company.slug)}" hx-target="#main-container" hx-swap="innerHTML">${company.name}</a>
  </td>
  <td>${company.city}</td>
  <td>${states.get(company.state)}</td>
  <td>${company.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>${company.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>
    % if company.count_recomended > 0:
    <span class="badge text-bg-success" role="button" hx-get="${request.route_url('company_recomended', company_id=company.id, slug=company.slug)}" hx-target="#main-container" hx-swap="innerHTML">${company.count_recomended}</span>
    % else:
    <span class="badge text-bg-secondary">0</span>
    % endif
  </td>
</tr>
% endfor