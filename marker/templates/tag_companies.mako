<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="tag_pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(tag)}</div>
  <div>${button.a_btn(icon='map', color='secondary', url=request.route_url('tag_map_companies', tag_id=tag.id, slug=tag.slug))}</div>
</div>

<%include file="tag_lead.mako"/>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown(dd_filter, url=request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug))}</div>
  <div>${button.dropdown(dd_sort, url=request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug))}</div>
  <div class="me-auto">${button.dropdown(dd_order, url=request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug))}</div>
  <div>${button.a_btn(icon='download', color='primary', url=request.route_url('tag_export_companies', tag_id=tag.id, slug=tag.slug, _query={'filter': dd_filter._filter, 'sort': dd_sort._sort, 'order': dd_order._order}))}</div>
</div>

<%include file="company_table.mako"/>