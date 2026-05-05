<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-briefcase"></i> ${_("Projects")}
  <span class="badge bg-secondary">${len(items)}</span>
  <div class="float-end">
    ${button.a(icon='search', color='primary', url=request.route_url('project_search'))}
    ${button.a(icon='plus-lg', color='success', url=request.route_url('project_add'))}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-3 d-flex flex-wrap align-items-center">
  <div class="btn-group btn-group-sm ms-auto" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-outline-primary" href="${request.route_url('project_all')}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('project_map')}"><i class="bi bi-map"></i> ${_("Map")}</a>
    <a class="btn btn-primary" href="${request.route_url('project_uptime')}"><i class="bi bi-globe"></i> ${_("Uptime")}</a>
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
    % for i, item in enumerate(items, 1):
    <tr>
      <td>${i}</td>
      <td>${item['name']}</td>
      <td class="text-break"><a href="${item['website'] if item['website'].startswith(('http://', 'https://')) else 'https://' + item['website']}" target="_blank" rel="noopener">${item['website']}</a></td>
      <td hx-get="${request.route_url('project_uptime_check', _query={'url': item['website']})}"
          hx-trigger="load"
          hx-swap="innerHTML">
        <div class="spinner-border spinner-border-sm" role="status"><span class="visually-hidden">Loading...</span></div>
      </td>
    </tr>
    % endfor
  </tbody>
</table>
</div>
