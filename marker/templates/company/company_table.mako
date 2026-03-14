<%namespace name="checkbox" file="checkbox.mako"/>

<%
  show_shared_tags = bool(context.get("show_shared_tags", False))
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