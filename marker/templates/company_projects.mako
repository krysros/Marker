<%inherit file="layout.mako"/>
<%namespace name="pills" file="pills.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(company_pills)}</div>
  <div>
    % if request.identity.role == 'editor' or 'admin':
    ${button.a_button(icon='plus-lg', color='success', url=request.route_url('company_add_project', company_id=company.id, slug=company.slug))}
    % else:
    <button type="button" class="btn btn-success" disabled><i class="bi bi-plus-lg"></i></button>
    % endif
  </div>
</div>

<%include file="company_lead.mako"/>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>#</th>
        <th>${_("Project")}</th>
        <th>${_("Stage")}</th>
        <th>${_("Role")}</th>
        <th>${_("Action")}</th>
      </tr>
    </thead>
    <tbody id="new-assoc">
      % for assoc in company.projects:
        <%include file="project_row.mako" args="assoc=assoc"/>
      % endfor
    </tbody>
  </table>
</div>