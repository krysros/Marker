<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="tag_pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(tag)}</div>
  <div>${button.button('tag_map_projects', color='secondary', icon='map', tag_id=tag.id, slug=tag.slug)}</div>
</div>

<%include file="tag_lead.mako"/>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('tag_projects', dd_filter, tag_id=tag.id, slug=tag.slug)}</div>
  <div>${button.dropdown('tag_projects', dd_sort, tag_id=tag.id, slug=tag.slug)}</div>
  <div class="me-auto">${button.dropdown('tag_projects', dd_order, tag_id=tag.id, slug=tag.slug)}</div>
  <div>${button.button('tag_export_projects', color='primary', icon='download', tag_id=tag.id, slug=tag.slug, _query={'filter': dd_filter._filter, 'sort': dd_sort._sort, 'order': dd_order._order})}</div>
</div>

<%include file="project_table.mako"/>