<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div class="me-auto">${pills.pills(tag_pills, active_url=request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug))}</div>
  <div>${button.a(icon='map', color='secondary', url=request.route_url('tag_map_companies', tag_id=tag.id, slug=tag.slug, _query=q))}</div>
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

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <%include file="company_filter.mako"/>
  <div>${button.dropdown_filter('role', _("Role"), role_choices)}</div>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div class="me-auto">${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="company_table.mako"/>