<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="tag_pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(tag)}</div>
  <div>${button.button('tag_projects', color='secondary', icon='table', tag_id=tag.id, slug=tag.slug)}</div>
</div>

<%include file="tag_lead.mako"/>

<div id="map"></div>

<%include file="markers.mako"/>