<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div id="main-container" hx-boost="true" hx-target="#main-container" hx-select="#main-container" hx-swap="outerHTML" hx-push-url="true">
<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <div class="me-auto">${pills.pills(tag_pills, active_url=request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug))}</div>
</div>

<%include file="tag_lead.mako"/>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <%include file="company_filter.mako"/>
  ${button.dropdown_filter('role', _("Role"), role_choices)}
  <div class="vr mx-1"></div>
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
  <div class="vr mx-1"></div>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}" hx-boost="false">
    <a class="btn btn-outline-primary" href="${request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug, _query=q)}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('tag_map_companies', tag_id=tag.id, slug=tag.slug, _query=q)}"><i class="bi bi-map"></i> ${_("Map")}</a>
  </div>
  <div class="vr mx-1"></div>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}" hx-boost="false">
    <a class="btn btn-primary" href="${request.route_url('tag_uptime_companies', tag_id=tag.id, slug=tag.slug, _query=q)}"><i class="bi bi-globe"></i> ${_("Uptime")}</a>
    <a class="btn ${'btn-primary' if q.get('duplicates') == '1' else 'btn-outline-primary'}" href="${request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug, _query={**q, 'duplicates': '1', 'no_location': None})}"><i class="bi bi-files"></i> ${_("Duplicates")}</a>
    <a class="btn ${'btn-primary' if q.get('no_location') == '1' else 'btn-outline-primary'}" href="${request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug, _query={**q, 'duplicates': None, 'no_location': '1'})}"><i class="bi bi-geo"></i> ${_("No location")}</a>
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
</div>
