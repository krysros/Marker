<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>

<%!
  def fmt_decimal(value):
      if value is None:
          return "---"
      formatted = f"{value:,.2f}"
      formatted = formatted.replace(",", "\u202f")
      return formatted
%>

<%
  show_shared_tags = bool(context.get("show_shared_tags", False))
  shared_tag_counts = context.get("shared_tag_counts", {})
  shared_tag_labels = context.get("shared_tag_labels", {})
  activity_values = context.get("activity_values")
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
  <td>${checkbox.checkbox(company, selected_ids=selected_ids('selected_companies'), url=request.route_url('company_check', company_id=company.id, slug=company.slug))}</td>
  <td>
    <a href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">${company.name}</a><br>
    <small class="text-body-secondary">${_("Created at")}: ${company.created_at.strftime('%Y-%m-%d %H:%M:%S')}</small><br>
    <small class="text-body-secondary">${_("Updated at")}: ${company.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</small>
  </td>
  <td>
    ${company.city or "---"}<br>
    <small class="text-body-secondary">${get_subdivision_name(company.subdivision, "---")}</small><br>
    <small class="text-body-secondary">${get_country_name(company.country, "---")}</small>
  </td>
  % if show_shared_tags:
  <td>
    <span class="badge text-bg-info"
          role="button"
          tabindex="0"
          data-bs-toggle="popover"
          data-bs-trigger="hover focus"
          data-bs-placement="top"
          data-bs-title="${_("Common tags")}" 
          data-bs-content="${shared_tag_labels.get(company.id, '')}">
      ${shared_tag_counts.get(company.id, 0)}
    </span>
  </td>
  % endif
  <td>
    <a href="${request.route_url('company_projects', company_id=company.id, slug=company.slug)}">
      <span class="badge text-bg-secondary" role="button">${company.count_projects}</span>
    </a>
  </td>
  % if activity_values is not None:
  <%
    av = activity_values.get(company.id)
  %>
  <td class="text-end">${fmt_decimal(av.value_net if av else None)}</td>
  <td class="text-end">${fmt_decimal(av.value_gross if av else None)}</td>
  % endif
  <td>
    <a href="${request.route_url('company_stars', company_id=company.id, slug=company.slug)}"
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
      ${button.a(icon='pencil-square', color='warning', size='sm', url=request.route_url('company_edit', company_id=company.id, slug=company.slug))}
      ${button.del_row(icon='trash', color='danger', size='sm', url=request.route_url('company_del_row', company_id=company.id, slug=company.slug))}
    </div>
  </td>
</tr>
% endfor
