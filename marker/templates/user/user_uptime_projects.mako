<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <div class="me-auto">${pills.pills(user_pills, active_url=request.route_url('user_projects', username=user.name))}</div>
</div>

<p class="lead">${user.fullname}</p>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-outline-primary" href="${request.route_url('user_projects', username=user.name)}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_map_projects', username=user.name)}"><i class="bi bi-map"></i> ${_("Map")}</a>
    <a class="btn btn-primary" href="${request.route_url('user_uptime_projects', username=user.name)}"><i class="bi bi-globe"></i> ${_("Uptime")}</a>
  </div>
</div>

<div class="table-responsive">
<table class="table table-striped">
  <thead>
    <tr>
      <th>#</th>
      <th>${_("Name")}</th>
      <th>${_("Website")}</th>
      <th>${_("HTTP response code")}</th>
    </tr>
  </thead>
  <tbody id="uptime-tbody">
    <%include file="user_uptime_projects_rows.mako"/>
  </tbody>
</table>
</div>
