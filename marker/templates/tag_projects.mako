<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(tag_pills)}</div>
  <div>${button.a_button(icon='map', color='secondary', url=request.route_url('tag_map_projects', tag_id=tag.id, slug=tag.slug))}</div>
</div>

<%include file="tag_lead.mako"/>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown(dd_filter)}</div>
  <div>${button.dropdown(dd_sort)}</div>
  <div class="me-auto">${button.dropdown(dd_order)}</div>
  <div>${button.a_button(icon='download', color='primary', url=request.route_url('tag_export_projects', tag_id=tag.id, slug=tag.slug, _query={'filter': dd_filter._filter, 'sort': dd_sort._sort, 'order': dd_order._order}))}</div>
</div>

<%include file="project_table.mako"/>