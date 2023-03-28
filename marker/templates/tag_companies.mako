<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.tag_pill(tag)}</div>
  <div>${button.map('tag_map_companies', tag_id=tag.id, slug=tag.slug)}</div>
</div>

<%include file="tag_lead.mako"/>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('tag_companies', dd_filter, tag_id=tag.id, slug=tag.slug)}</div>
  <div>${button.dropdown('tag_companies', dd_sort, tag_id=tag.id, slug=tag.slug)}</div>
  <div class="me-auto">${button.dropdown('tag_companies', dd_order, tag_id=tag.id, slug=tag.slug)}</div>
  <div>${button.export('tag_export_companies', tag_id=tag.id, slug=tag.slug, _query={'filter': dd_filter._filter, 'sort': dd_sort._sort, 'order': dd_order._order})}</div>
</div>

<%include file="company_table.mako"/>