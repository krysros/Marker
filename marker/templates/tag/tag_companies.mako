<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="d-flex flex-nowrap overflow-x-auto align-items-center gap-2 mb-4 pb-1">
  <div class="me-auto">${pills.pills(tag_pills, active_url=request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug))}</div>
  <% from marker.utils.export_columns import tag_company_cols; _export_cols = tag_company_cols(_) %>
  <div>${button.dropdown_download_cols(request.route_url('tag_export_companies', tag_id=tag.id, slug=tag.slug, _query=q), _export_cols)}</div>
  <div>
    % if request.identity.role == 'editor' or 'admin':
    ${button.a(icon='plus-lg', color='success', url=request.route_url('tag_add_company', tag_id=tag.id, slug=tag.slug))}
    % else:
    <button type="button" class="btn btn-success" disabled><i class="bi bi-plus-lg"></i></button>
    % endif
  </div>
</div>

<%include file="tag_lead.mako"/>

<div class="d-flex flex-nowrap overflow-x-auto align-items-center gap-2 mb-4 pb-1">
  <%include file="company_filter.mako"/>
  ${button.dropdown_filter('role', _("Role"), role_choices)}
  <div class="vr mx-1"></div>
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
  <div class="vr mx-1"></div>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-primary" href="${request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug, _query=q)}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('tag_map_companies', tag_id=tag.id, slug=tag.slug, _query=q)}"><i class="bi bi-map"></i> ${_("Map")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('tag_uptime_companies', tag_id=tag.id, slug=tag.slug)}"><i class="bi bi-globe"></i> ${_("Uptime")}</a>
  </div>
</div>

<%include file="company_table.mako"/>