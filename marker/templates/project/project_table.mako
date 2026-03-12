<%namespace name="checkbox" file="checkbox.mako"/>

<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th>${checkbox.select_all()}</th>
        <th>${_("Project")}</th>
        <th>${_("City")}</th>
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