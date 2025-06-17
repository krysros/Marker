<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(company_pills)}</div>
  <div>
    % if request.identity.role == 'editor' or 'admin':
    ${button.a_button(icon='plus-lg', color='success', url=request.route_url('company_add_contact', company_id=company.id, slug=company.slug))}
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
        <th>${_("Fullname")}</th>
        <th>${_("Role")}</th>
        <th>${_("Phone")}</th>
        <th>${_("Email")}</th>
        <th>${_("Action")}</th>
      </tr>
    </thead>
    <tbody id="new-contact">
      % for contact in company.contacts:
        <%include file="contact_row.mako" args="contact=contact"/>
      % endfor
    </tbody>
  </table>
</div>
