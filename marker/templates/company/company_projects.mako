<%inherit file="layout.mako"/>
<%namespace name="pills" file="pills.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <div class="me-auto">${pills.pills(company_pills)}</div>
  <div>
    % if request.identity.role == 'editor' or 'admin':
    <a href="${request.route_url('company_add_project', company_id=company.id, slug=company.slug)}" class="btn btn-success"><i class="bi bi-plus-lg"></i></a>
    % else:
    <button type="button" class="btn btn-success" disabled><i class="bi bi-plus-lg"></i></button>
    % endif
  </div>
</div>

<%include file="company_lead.mako"/>

<%
  role_q = {k: v for k, v in q.items() if k not in ('country', 'subdivision', 'city')}
  role_q['mode'] = 'role'
  if role_q.get('sort') in ('city', 'distance'):
      role_q.pop('sort', None)
      role_q.pop('order', None)

  loc_q = {k: v for k, v in q.items() if k not in ('stage', 'role')}
  loc_q['mode'] = 'location'
  if loc_q.get('sort') in ('stage', 'role', 'created_at', 'updated_at'):
      loc_q.pop('sort', None)
      loc_q.pop('order', None)
%>

% if q.get('mode') == 'location':
<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <div class="dropdown">
    <button type="button" class="btn btn-sm btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" data-bs-auto-close="outside">
      % if q.get('country') or q.get('subdivision'):
        <i class="bi bi-geo-alt-fill"></i>
      % else:
        <i class="bi bi-geo-alt"></i>
      % endif
      ${_("Location")}
    </button>
    <form class="dropdown-menu p-3" style="min-width: 300px;">
      ${preserve_params({'country', 'subdivision'})}
      <div class="mb-3">
        ${form.country.label(class_="form-label")}
        ${form.country(class_="form-control", **{"hx-get": f"{request.route_url('subdivision')}", "hx-target": "#subdivision"})}
      </div>
      <div class="mb-3">
        ${form.subdivision.label(class_="form-label")}
        ${form.subdivision(class_="form-control")}
        <small class="text-body-secondary">Ctrl + Click</small>
      </div>
      <div class="hstack gap-2">
        <button type="submit" class="btn btn-primary btn-sm">${_("Submit")}</button>
        <% clear_q = {k: v for k, v in q.items() if k not in ('country', 'subdivision')} %>
        <a class="btn btn-outline-secondary btn-sm" href="${request.current_route_url(_query=clear_q)}">${_("Clear")}</a>
      </div>
    </form>
  </div>

  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
  <div class="vr align-self-stretch my-1 mx-1"></div>
  <div class="btn-group" role="group">
    <a href="${request.current_route_url(_query=role_q)}" class="btn btn-sm btn-${'primary' if q.get('mode') != 'location' else 'outline-primary'}">Rola</a>
    <a href="${request.current_route_url(_query=loc_q)}" class="btn btn-sm btn-${'primary' if q.get('mode') == 'location' else 'outline-primary'}">Lokalizacja</a>
  </div>
</div>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>${checkbox.select_all()}</th>
        <th>${_("Project")}</th>
        <th>${_("City")}</th>
        <th>${_("Distance")}</th>
        <th>${_("Action")}</th>
      </tr>
    </thead>
    <tbody id="new-assoc">
      % for assoc in projects_assoc:
        <tr>
          <td>
            ${checkbox.checkbox(assoc.project, selected_ids=selected_ids('selected_projects'), url=request.route_url('project_check', project_id=assoc.project.id, slug=assoc.project.slug))}
          </td>
          <td>
            <a href="${request.route_url('project_view', project_id=assoc.project.id, slug=assoc.project.slug)}">
              ${assoc.project.name}
            </a><br/>
            <small class="text-body-secondary">${_("Created at")}: ${assoc.project.created_at.strftime('%Y-%m-%d %H:%M:%S') if assoc.project.created_at else '---'}</small><br/>
            <small class="text-body-secondary">${_("Updated at")}: ${assoc.project.updated_at.strftime('%Y-%m-%d %H:%M:%S') if assoc.project.updated_at else '---'}</small>
          </td>
          <td>
            ${assoc.project.city or "—"}<br/>
            <small class="text-body-secondary">${get_subdivision_name(assoc.project.subdivision, "—")}</small><br/>
            <small class="text-body-secondary">${get_country_name(assoc.project.country, "—")}</small>
          </td>
          <td>
            % if assoc.distance_km is not None:
              ${"{:.2f}".format(assoc.distance_km)} km
            % else:
              <span class="text-muted">N/A</span>
            % endif
          </td>
          <td>
            <div class="hstack gap-2">
              ${button.project_star(assoc.project, size='sm')}
              ${button.a(icon='pencil-square', color='warning', size='sm', url=request.route_url('project_activity_edit', project_id=assoc.project.id, company_id=assoc.company.id))}
              ${button.del_row(icon='dash-lg', color='danger', size='sm', url=request.route_url('activity_unlink', project_id=assoc.project.id, company_id=assoc.company.id))}
            </div>
          </td>
        </tr>
      % endfor
    </tbody>
  </table>
</div>
% else:
<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  ${button.dropdown_filter('stage', _('Stage'), filter_stages)}
  ${button.dropdown_filter('role', _('Role'), filter_roles)}
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
  <div class="vr align-self-stretch my-1 mx-1"></div>
  <div class="btn-group" role="group">
    <a href="${request.current_route_url(_query=role_q)}" class="btn btn-sm btn-${'primary' if q.get('mode') != 'location' else 'outline-primary'}">Rola</a>
    <a href="${request.current_route_url(_query=loc_q)}" class="btn btn-sm btn-${'primary' if q.get('mode') == 'location' else 'outline-primary'}">Lokalizacja</a>
  </div>
</div>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>${checkbox.select_all()}</th>
        <th>${_("Project")}</th>
        <th>${_("Stage")}</th>
        <th>${_("Role")}</th>
        <th>${_("Value")}</th>
        <th>${_("Price per m²")}</th>
        <th>${_("Action")}</th>
      </tr>
    </thead>
    <tbody id="new-assoc">
      % for assoc in projects_assoc:
        <%include file="project_row.mako" args="assoc=assoc"/>
      % endfor
    </tbody>
  </table>
</div>
% endif

<%def name="preserve_params(exclude)">
<%
  skip = set(exclude)
%>
% for k, v in q.items():
  % if k not in skip:
    % if isinstance(v, list):
      % for item in v:
        <input type="hidden" name="${k}" value="${item}">
      % endfor
    % elif v is not None and str(v) != '':
      <input type="hidden" name="${k}" value="${v}">
    % endif
  % endif
% endfor
</%def>