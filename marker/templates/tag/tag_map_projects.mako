<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="d-flex flex-nowrap overflow-x-auto align-items-center gap-2 mb-4 pb-1">
  <div class="me-auto">${pills.pills(tag_pills, active_url=request.route_url('tag_projects', tag_id=tag.id, slug=tag.slug))}</div>
  <% from marker.utils.export_columns import tag_project_cols; _export_cols = tag_project_cols(_) %>
  <div>${button.dropdown_download_cols(request.route_url('tag_export_projects', tag_id=tag.id, slug=tag.slug, _query=q), _export_cols)}</div>
</div>

<%include file="tag_lead.mako"/>

<div class="d-flex flex-nowrap overflow-x-auto align-items-center gap-2 mb-4 pb-1">
  <div class="btn-group btn-group-sm ms-auto" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-outline-primary" href="${request.route_url('tag_projects', tag_id=tag.id, slug=tag.slug, _query=q)}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-primary" href="${request.route_url('tag_map_projects', tag_id=tag.id, slug=tag.slug, _query=q)}"><i class="bi bi-map"></i> ${_("Map")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('tag_uptime_projects', tag_id=tag.id, slug=tag.slug)}"><i class="bi bi-globe"></i> ${_("Uptime")}</a>
  </div>
</div>

<div id="map"></div>

<%include file="markers.mako"/>