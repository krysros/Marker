% for row in paginator:
% if loop.last:
<tr hx-get="${next_page}" hx-trigger="revealed" hx-swap="afterend">
% else:
<tr>
% endif
  <td>
    <a href="${request.route_url('project_view', project_id=row.project.id, slug=row.project.slug)}">${row.project.name}</a>
    % if row.project.usable_area:
    <br><small class="text-body-secondary">${_("Usable area")}: ${"{:,.2f}".format(row.project.usable_area)} m2</small>
    % endif
  </td>
  <td><small>${object_categories.get(row.project.object_category, row.project.object_category or "---")}</small></td>
  <td>
    <a href="${request.route_url('company_view', company_id=row.company.id, slug=row.company.slug)}">${row.company.name}</a>
  </td>
  <td>${stages.get(row.activity.stage, row.activity.stage or "---")}</td>
  <td>${roles.get(row.activity.role, row.activity.role or "---")}</td>
  <td>${row.activity.currency or "---"}</td>
  <td class="text-end">
    % if row.activity.value_net is not None:
    ${"{:,.2f}".format(row.activity.value_net)}
    % else:
    ---
    % endif
  </td>
  <td class="text-end">
    % if row.activity.value_gross is not None:
    ${"{:,.2f}".format(row.activity.value_gross)}
    % else:
    ---
    % endif
  </td>
  <td class="text-end">
    % if row.unit_price_net is not None:
    ${"{:,.2f}".format(row.unit_price_net)}
    % else:
    ---
    % endif
  </td>
  <td class="text-end">
    % if row.unit_price_gross is not None:
    ${"{:,.2f}".format(row.unit_price_gross)}
    % else:
    ---
    % endif
  </td>
</tr>
% endfor
