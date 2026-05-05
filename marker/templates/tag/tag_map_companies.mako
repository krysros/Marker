<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div class="me-auto">${pills.pills(tag_pills, active_url=request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug))}</div>
  <div>${button.a(icon='table', color='secondary', url=request.route_url('tag_companies', tag_id=tag.id, slug=tag.slug, _query=q))}</div>
  <% _contact_cols = [_('Contact name'), _('Contact role'), _('Contact phone'), _('Contact email')]; _export_cols = _contact_cols + [_('Tag')] + [_('Company name'), _('Company street'), _('Company post code'), _('Company city'), _('Company subdivision'), _('Company country'), _('Company website'), _('Company NIP'), _('Company REGON'), _('Company KRS'), _('Tags')] %>
  <div>${button.dropdown_download_cols(request.route_url('tag_export_companies', tag_id=tag.id, slug=tag.slug, _query=q), _export_cols)}</div>
</div>

<%include file="tag_lead.mako"/>

<div id="map"></div>

<%include file="markers.mako"/>