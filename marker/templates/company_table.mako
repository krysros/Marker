<div class="table-responsive">
  <table class="table table-striped">
    <thead>
      <tr>
        <th class="col-1">#</th>
        <th>${_("Company")}</th>
        <th>${_("City")}</th>
        <th>${_("Region")}</th>
        <th>${_("Created at")}</th>
        <th>${_("Updated at")}</th>
        <th>${_("Recommended")}</th>
        <th>${_("Comments")}</th>
        <th class="col-2">${_("Action")}</th>
      </tr>
    </thead>
    <tbody>
      <%include file="company_more.mako"/>
    </tbody>
  </table>
</div>