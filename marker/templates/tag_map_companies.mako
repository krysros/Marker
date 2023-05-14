<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(tag_pills, active_url=request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug))}</div>
  <div>${button.a_button(icon='table', color='secondary', url=request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug, _query=q))}</div>
  <div>${button.a_button(icon='download', color='primary', url=request.route_url('tag_export_companies', tag_id=tag.id, slug=tag.slug, _query=q))}</div>
</div>

<%include file="tag_lead.mako"/>

<div id="map"></div>

<%include file="markers.mako"/>