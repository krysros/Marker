<%inherit file="layout.mako"/>
<%namespace name="pills" file="pills.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div class="me-auto">${pills.pills(project_pills)}</div>
  <div>
    % if request.identity.role == 'editor' or 'admin':
    ${button.a(icon='plus-lg', color='success', url=request.route_url('project_add_company', project_id=project.id, slug=project.slug))}
    % else:
    <button type="button" class="btn btn-success" disabled><i class="bi bi-plus-lg"></i></button>
    % endif
  </div>
</div>

<%include file="project_lead.mako"/>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div>${button.dropdown_filter('stage', _('Stage'), filter_stages)}</div>
  <div>${button.dropdown_filter('role', _('Role'), filter_roles)}</div>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>${checkbox.select_all()}</th>
        <th>${_("Company")}</th>
        <th>${_("Stage")}</th>
        <th>${_("Role")}</th>
        <th>${_("Net value")}</th>
        <th>${_("Gross value")}</th>
        <th>${_("Net price per m² of usable area")}</th>
        <th>${_("Gross price per m² of usable area")}</th>
        <th>${_("Created at")}</th>
        <th>${_("Updated at")}</th>
        <th>${_("Action")}</th>
      </tr>
    </thead>
    <tbody id="new-assoc">
      % for assoc in companies_assoc:
        <%include file="company_row.mako" args="assoc=assoc"/>
      % endfor
    </tbody>
  </table>
</div>
