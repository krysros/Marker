<%inherit file="layout.mako"/>
<%namespace name="pills" file="pills.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <div class="me-auto">${pills.pills(project_pills)}</div>
% if request.identity.role == 'editor' or 'admin':
  <a href="${request.route_url('project_add_company', project_id=project.id, slug=project.slug)}" class="btn btn-success"><i class="bi bi-plus-lg"></i></a>
% else:
  <button type="button" class="btn btn-success" disabled><i class="bi bi-plus-lg"></i></button>
% endif
</div>

<%include file="project_lead.mako"/>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  ${button.dropdown_filter('stage', _('Stage'), filter_stages)}
  ${button.dropdown_filter('role', _('Role'), filter_roles)}
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
</div>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>${checkbox.select_all()}</th>
        <th>${_("Company")}</th>
        <th>${_("Stage")}</th>
        <th>${_("Role")}</th>
        <th>${_("Value")}</th>
        <th>${_("Price per m²")}</th>
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
