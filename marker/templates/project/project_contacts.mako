<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>
<%namespace name="checkbox" file="checkbox.mako"/>
<%namespace name="ct" file="contact_table.mako"/>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div class="me-auto">${pills.pills(project_pills)}</div>
  <div>
    % if request.identity.role == 'editor' or 'admin':
    ${button.a(icon='plus-lg', color='success', url=request.route_url('project_add_contact', project_id=project.id, slug=project.slug))}
    % else:
    <button type="button" class="btn btn-success" disabled><i class="bi bi-plus-lg"></i></button>
    % endif
  </div>
</div>

<%include file="project_lead.mako"/>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>${checkbox.select_all()}</th>
        <th>${_("Fullname")}</th>
        <th>${_("Role")}</th>
        <th>${_("Phone")}</th>
        <th>${_("Email")}</th>
        <th>${_("Projects")}</th>
        <th>${_("City")}</th>
        <th>${_("Action")}</th>
      </tr>
    </thead>
    <tbody id="new-contact">
      ${ct.rows(paginator=contacts)}
    </tbody>
  </table>
</div>
