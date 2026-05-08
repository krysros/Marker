<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="d-flex flex-nowrap overflow-x-auto align-items-center gap-2 mb-4 pb-1">
  <div class="me-auto">${pills.pills(tag_pills, active_url=request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug))}</div>
</div>

<%include file="tag_lead.mako"/>

<div class="d-flex flex-nowrap overflow-x-auto align-items-center gap-2 mb-4 pb-1">
  <div class="btn-group btn-group-sm ms-auto" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-outline-primary" href="${request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug)}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('tag_map_companies', tag_id=tag.id, slug=tag.slug)}"><i class="bi bi-map"></i> ${_("Map")}</a>
    <a class="btn btn-primary" href="${request.route_url('tag_uptime_companies', tag_id=tag.id, slug=tag.slug)}"><i class="bi bi-globe"></i> ${_("Uptime")}</a>
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
    <%include file="tag_uptime_companies_rows.mako"/>
  </tbody>
</table>
</div>
