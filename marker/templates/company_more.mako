<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>

<%!
  import pycountry
%>

% for company in paginator:
% if loop.last:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend"
    class="table-${company.color}">
% else:
<tr class="table-${company.color}">
% endif
  <td>${checkbox.checkbox(company, selected=request.identity.selected_companies, url=request.route_url('company_check', company_id=company.id, slug=company.slug))}</td>
  <td>
    <a href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">${company.name}</a>
  </td>
  <td>${company.city or "---"}</td>
  <td>${getattr(pycountry.subdivisions.get(code=company.subdivision), "name", "---")}</td>
  <td>${company.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>${company.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</td>
  <td>
    <a href="${request.route_url('company_recommended', company_id=company.id, slug=company.slug)}">
      <div hx-get="${request.route_url('company_count_recommended', company_id=company.id, slug=company.slug)}"
           hx-trigger="recommendEvent from:body"
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
    ${button.a_button(icon='pencil-square', color='warning', size='sm', url=request.route_url('company_edit', company_id=company.id, slug=company.slug))}
    ${button.del_row(icon='trash', color='danger', size='sm', url=request.route_url('company_del_row', company_id=company.id, slug=company.slug))}
  </td>
</tr>
% endfor
