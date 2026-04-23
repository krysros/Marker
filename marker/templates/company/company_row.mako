<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>
<%page args="assoc"/>

<%!
  def fmt_decimal(value):
      if value is None:
          return "---"
      formatted = f"{value:,.2f}"
      formatted = formatted.replace(",", "\u202f")
      return formatted
%>

% if assoc:
<tr>
  <td>${checkbox.checkbox(assoc.company, selected_ids=selected_ids('selected_companies'), url=request.route_url('company_check', company_id=assoc.company.id, slug=assoc.company.slug))}</td>
  <td>
    <a href="${request.route_url('company_view', company_id=assoc.company.id, slug=assoc.company.slug)}">${assoc.company.name}</a>
    <div class="small text-muted">
      ${_("Created at")}: ${assoc.company.created_at.strftime('%Y-%m-%d %H:%M:%S') if assoc.company.created_at else '---'}<br/>
      ${_("Updated at")}: ${assoc.company.updated_at.strftime('%Y-%m-%d %H:%M:%S') if assoc.company.updated_at else '---'}
    </div>
  </td>
  <td>${stages.get(assoc.stage)}</td>
  <td>${company_roles.get(assoc.role)}</td>
  <td>
    <span class="d-block">${_("Net")}: ${fmt_decimal(assoc.value_net)}</span>
    <span class="d-block">${_("Gross")}: ${fmt_decimal(assoc.value_gross)}</span>
  </td>
  <td>
    <span class="d-block">${_("Net")}: ${fmt_decimal(assoc.value_net / assoc.project.usable_area) if assoc.value_net and assoc.project.usable_area else '---'}</span>
    <span class="d-block">${_("Gross")}: ${fmt_decimal(assoc.value_gross / assoc.project.usable_area) if assoc.value_gross and assoc.project.usable_area else '---'}</span>
  </td>
  <td>
    <div class="hstack gap-2 mx-2">
      ${button.company_star(assoc.company, size='sm')}
      ${button.a(icon='pencil-square', color='warning', size='sm', url=request.route_url('company_activity_edit', company_id=assoc.company.id, project_id=assoc.project.id))}
      ${button.del_row(icon='dash-lg', color='danger', size='sm', url=request.route_url('activity_unlink', company_id=assoc.company.id, project_id=assoc.project.id))}
    </div>
  </td>
</tr>
% endif