<%inherit file="layout.mako"/>
<%namespace name="pills" file="pills.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div class="me-auto">${pills.pills(company_pills)}</div>
  <div>
    % if request.identity.role == 'editor' or 'admin':
    ${button.a(icon='plus-lg', color='success', url=request.route_url('company_add_project', company_id=company.id, slug=company.slug))}
    % else:
    <button type="button" class="btn btn-success" disabled><i class="bi bi-plus-lg"></i></button>
    % endif
  </div>
</div>

<%include file="company_lead.mako"/>

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
        <th>${_("Project")}</th>
        <th>${_("Stage")}</th>
        <th>${_("Role")}</th>
        <th>${_("Wartość")}</th>
        <th>${_("Cena za m²")}</th>
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