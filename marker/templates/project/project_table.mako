<%namespace name="checkbox" file="checkbox.mako"/>

<%
  show_shared_tags = bool(context.get("show_shared_tags", False))
%>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>${checkbox.select_all()}</th>
        <th>${_("Project")}</th>
        <th>${_("Object category")}</th>
        <th>${_("City")}</th>
        % if show_shared_tags:
        <th>${_("Common tags")}</th>
        % endif
        <th>${_("Companies")}</th>
        <th>${_("Stars")}</th>
        <th>${_("Comments")}</th>
        <th>${_("Action")}</th>
      </tr>
    </thead>
    <tbody>
      <%include file="project_more.mako"/>
    </tbody>
  </table>
</div>