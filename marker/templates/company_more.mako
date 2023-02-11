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
           hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
           hx-trigger="click"
           hx-swap="none">
    % else:
    <input class="form-check-input"
           type="checkbox"
           value="${company.id}"
           autocomplete="off"
           hx-post="${request.route_url('company_check', company_id=company.id)}"
           hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}'
           hx-trigger="click"
           hx-swap="none">
    % endif
  </td>
  <td>
    % if company in request.identity.recommended:
    <i class="bi bi-hand-thumbs-up-fill"></i>
    % endif
    <a href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">${company.name}</a>
  </td>
  <td>${company.city or "---"}</td>
  <td>${regions.get(company.region) or "---"}</td>
  <td>${company.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>${company.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>
    % if company.count_recommended > 0:
    <a href="${request.route_url('company_recommended', company_id=company.id, slug=company.slug)}">
      <span class="badge text-bg-success" role="button">${company.count_recommended}</span>
    </a>
    % else:
    <span class="badge text-bg-secondary">0</span>
    % endif
  </td>
  <td>
    % if company.count_comments > 0:
    <a href="${request.route_url('company_comments', company_id=company.id, slug=company.slug)}">
      <span class="badge text-bg-dark" role="button">${company.count_comments}</span>
    </a>
    % else:
    <span class="badge text-bg-secondary">0</span>
    % endif
  </td>
</tr>
% endfor
