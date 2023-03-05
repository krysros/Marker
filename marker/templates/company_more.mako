<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>

% for company in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend"
    class="table-${company.color}">
% else:
<tr class="table-${company.color}">
% endif
  <td>${checkbox.company(company)}</td>
  <td>
    <a href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">${company.name}</a>
  </td>
  <td>${company.city or "---"}</td>
  <td>${regions.get(company.region) or "---"}</td>
  <td>${company.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>${company.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>
    <a href="${request.route_url('company_recommended', company_id=company.id, slug=company.slug)}">
      <div hx-get="${request.route_url('count_company_recommended', company_id=company.id, slug=company.slug)}"
            hx-trigger="recommendedCompanyEvent from:body"
            hx-target="#recommendations-${company.id}"
            hx-swap="innerHTML">
        <span id="recommendations-${company.id}" class="badge text-bg-secondary" role="button">${company.count_recommended}</swap>
      </div>
    </a>
  </td>
  <td>
    <a href="${request.route_url('company_comments', company_id=company.id, slug=company.slug)}">
      <span class="badge text-bg-secondary" role="button">${company.count_comments}</span>
    </a>
  </td>
  <td>
    ${button.recommend(company, size='sm')}
    ${button.edit('company_edit', company_id=company.id, slug=company.slug, size='sm')}
    ${button.delete('company_delete', company_id=company.id, slug=company.slug, size='sm')}
  </td>
</tr>
% endfor
