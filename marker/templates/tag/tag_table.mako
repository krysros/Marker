<%namespace name="checkbox" file="checkbox.mako"/>
<%
  category = q.get("category") if q else None
  show_companies = category != "projects"
  show_projects = category != "companies"
%>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>${checkbox.select_all()}</th>
        <th>${_("Tag")}</th>
        % if show_companies:
        <th>${_("Companies")}</th>
        % endif
        % if show_projects:
        <th>${_("Projects")}</th>
        % endif
        <th>${_("Action")}</th>
      </tr>
    </thead>
    <tbody>
      <%include file="tag_more.mako"/>
    </tbody>
  </table>
</div>