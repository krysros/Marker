<%namespace name="checkbox" file="/common/checkbox.mako"/>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>${checkbox.select_all()}</th>
        <th>${_("Name")}</th>
        <th>${_("Role")}</th>
        <th>${_("Phone")}</th>
        <th>${_("Email")}</th>
        % if q.get("category") == "companies":
        <th>${_("Company")}</th>
        % elif q.get("category") == "projects":
        <th>${_("Project")}</th>
        % else:
        <th>${_("Category")}</th>
        % endif
        <th>${_("City")}</th>
        <th>${_("Action")}</th>
      </tr>
    </thead>
    <tbody>
      <%include file="contact_more.mako"/>
    </tbody>
  </table>
</div>