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
    <a href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">${company.name}</a><br>
    <small class="text-body-secondary">${_("Created at")}: ${company.created_at.strftime('%Y-%m-%d %H:%M:%S')}</small><br>
    <small class="text-body-secondary">${_("Updated at")}: ${company.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</small>
  </td>
  <td>
    ${company.city or "---"}<br>
    <small class="text-body-secondary">${getattr(pycountry.subdivisions.get(code=company.subdivision), "name", "---")}</small><br>
    <small class="text-body-secondary">${getattr(pycountry.countries.get(alpha_2=company.country), "name", "---")}</small>
  </td>
  <td>
    <a href="${request.route_url('company_stars', company_id=company.id, slug=company.slug)}">
      <div hx-get="${request.route_url('company_count_stars', company_id=company.id, slug=company.slug)}"
           hx-trigger="starCompanyEvent from:body"
           hx-target="#companies-stars-${company.id}"
           hx-swap="innerHTML">
        <span id="companies-stars-${company.id}" class="badge text-bg-secondary" role="button">${company.count_stars}</swap>
      </div>
    </a>
  </td>
  <td>
    <a href="${request.route_url('company_comments', company_id=company.id, slug=company.slug)}">
      <span class="badge text-bg-secondary" role="button">${company.count_comments}</span>
    </a>
  </td>
  <td>
    <div class="hstack gap-2 mx-2">
      ${button.company_star(company, size='sm')}
      ${button.a_button(icon='pencil-square', color='warning', size='sm', url=request.route_url('company_edit', company_id=company.id, slug=company.slug))}
      ${button.del_row(icon='trash', color='danger', size='sm', url=request.route_url('company_del_row', company_id=company.id, slug=company.slug))}
    </div>
  </td>
</tr>
% endfor
