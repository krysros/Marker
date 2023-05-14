<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(tag_pills, active_url=request.route_url('tag_projects', tag_id=tag.id, slug=tag.slug))}</div>
  <div>${button.a_button(icon='map', color='secondary', url=request.route_url('tag_map_projects', tag_id=tag.id, slug=tag.slug, _query=q))}</div>
  <div>${button.a_button(icon='download', color='primary', url=request.route_url('tag_export_projects', tag_id=tag.id, slug=tag.slug, _query=q))}</div>
</div>

<%include file="tag_lead.mako"/>

<div class="hstack gap-2 mb-4">
  <%include file="project_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div class="me-auto">${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="project_table.mako"/>