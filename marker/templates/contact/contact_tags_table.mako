<%namespace name="checkbox" file="checkbox.mako"/>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>${checkbox.select_all()}</th>
        <th>${_("Name")}</th>
        <th>${_("Role")}</th>
        <th>${_("Phone")}</th>
        <th>${_("Email")}</th>
        <th>${_("Category")}</th>
        <th>${_("City")}</th>
        <th>${_("Action")}</th>
      </tr>
    </thead>
    <tbody>
      <%include file="contact_more.mako"/>
    </tbody>
  </table>
</div>
