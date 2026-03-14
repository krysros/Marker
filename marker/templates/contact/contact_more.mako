<%namespace name="button" file="/common/button.mako"/>
<%namespace name="checkbox" file="/common/checkbox.mako"/>
<%page args="paginator, next_page=None"/>

<%!
  import pycountry
%>

% for contact in paginator:
% if loop.last and next_page:
<tr hx-get="${next_page}"
    hx-trigger="revealed"
    hx-swap="afterend"
    class="table-${contact.color}">
% else:
<tr class="table-${contact.color}">
% endif
  <td>${checkbox.checkbox(contact, selected_ids=selected_ids('selected_contacts'), url=request.route_url('contact_check', contact_id=contact.id, slug=contact.slug))}</td>
  <td>
    <a href="${request.route_url('contact_view', contact_id=contact.id, slug=contact.slug)}">${contact.name or "---"}</a><br>
    <small class="text-body-secondary">${_("Created at")}: ${contact.created_at.strftime('%Y-%m-%d %H:%M:%S')}</small><br>
    <small class="text-body-secondary">${_("Updated at")}: ${contact.updated_at.strftime('%Y-%m-%d %H:%M:%S')}</small>
  </td>
  <td>
    ${contact.role or "---"}
  </td>
  <td>${contact.phone or "---"}</td>
  % if contact.email:
  <td><a href="mailto:${contact.email}">${contact.email}</a></td>
  % else:
  <td>---</td>
  % endif
  <td>
    % if contact.company:
    <i class="bi bi-buildings"></i> <a href="${request.route_url('company_view', company_id=contact.company.id, slug=contact.company.slug)}">${contact.company.name}</a><br>
    % elif contact.project:
    <i class="bi bi-briefcase"></i> <a href="${request.route_url('project_view', project_id=contact.project.id, slug=contact.project.slug)}">${contact.project.name}</a><br>
    % else:
    ---
    % endif
  </td>
  <td>
    % if contact.company:
    ${contact.company.city or "---"}<br>
    <small class="text-body-secondary">${getattr(pycountry.subdivisions.get(code=contact.company.subdivision), "name", "---")}</small><br>
    <small class="text-body-secondary">${getattr(pycountry.countries.get(alpha_2=contact.company.country), "name", "---")}</small>
  </td>
  % elif contact.project:
  <td>
    ${contact.project.city or "---"}<br>
    <small class="text-body-secondary">${getattr(pycountry.subdivisions.get(code=contact.project.subdivision), "name", "---")}</small><br>
    <small class="text-body-secondary">${getattr(pycountry.countries.get(alpha_2=contact.project.country), "name", "---")}</small>
  </td>
  % endif
  <td>
    <div class="hstack gap-2 mx-2">
      ${button.a(icon='person-vcard', color='primary', size='sm', url=request.route_url('contact_vcard', contact_id=contact.id, slug=contact.slug))}
      ${button.a(icon='pencil-square', color='warning', size='sm', url=request.route_url('contact_edit', contact_id=contact.id, slug=contact.slug))}
      ${button.del_row(icon='trash', color='danger', size='sm', url=request.route_url('contact_del_row', contact_id=contact.id, slug=contact.slug))}
    </div>
  </td>
</tr>
% endfor