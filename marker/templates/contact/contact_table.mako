<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>#</th>
        <th>${_("Name")}</th>
        <th>${_("Role")}</th>
        <th>${_("Phone")}</th>
        <th>${_("Email")}</th>
        % if q["parent"] == "companies":
        <th>${_("Company")}</th>
        % elif q["parent"] == "projects":
        <th>${_("Project")}</th>
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