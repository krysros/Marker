<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="d-flex flex-nowrap overflow-x-auto align-items-center gap-2 mb-4 pb-1">
  <div class="me-auto">${pills.pills(tag_pills, active_url=request.route_url('tag_projects', tag_id=tag.id, slug=tag.slug))}</div>
  <div>${button.a(icon='map', color='secondary', url=request.route_url('tag_map_projects', tag_id=tag.id, slug=tag.slug, _query=q))}</div>
  <% from marker.utils.export_columns import tag_project_cols; _export_cols = tag_project_cols(_) %>
  <div>${button.dropdown_download_cols(request.route_url('tag_export_projects', tag_id=tag.id, slug=tag.slug, _query=q), _export_cols)}</div>
  <div>
    % if request.identity.role == 'editor' or 'admin':
    ${button.a(icon='plus-lg', color='success', url=request.route_url('tag_add_project', tag_id=tag.id, slug=tag.slug))}
    % else:
    <button type="button" class="btn btn-success" disabled><i class="bi bi-plus-lg"></i></button>
    % endif
  </div>
</div>

<%include file="tag_lead.mako"/>

<div class="d-flex flex-nowrap overflow-x-auto align-items-center gap-2 mb-4 pb-1">
  <%include file="project_filter.mako"/>
  ${button.dropdown_filter('role', _("Role"), role_choices)}
  <div class="vr mx-1"></div>
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
</div>

<%include file="project_table.mako"/>