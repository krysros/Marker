<%namespace name="checkbox" file="checkbox.mako"/>

<%
  show_shared_tags = bool(context.get("show_shared_tags", False))
  activity_values = context.get("activity_values")
%>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>${checkbox.select_all()}</th>
        <th>${_("Company")}</th>
        <th>${_("City")}</th>
        % if show_shared_tags:
        <th>${_("Common tags")}</th>
        % endif
        <th>${_("Projects")}</th>
        % if activity_values is not None:
        <th class="text-end">${_("Value net")}</th>
        <th class="text-end">${_("Value gross")}</th>
        % endif
        <th>${_("Stars")}</th>
        <th>${_("Comments")}</th>
        <th>${_("Action")}</th>
      </tr>
    </thead>
    <tbody>
      <%include file="company_more.mako"/>
    </tbody>
  </table>
</div>