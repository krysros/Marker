<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-star"></i> ${_("Stars")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a(icon='table', color='secondary', url=request.route_url('user_companies_stars', username=user.name))}
    ${button.button(icon='star', color='warning', url=request.route_url('user_clear_companies_stars', username=user.name))}
    <% _contact_cols = [_('Contact name'), _('Contact role'), _('Contact phone'), _('Contact email')]; _export_cols = _contact_cols + [_('Company name'), _('Company street'), _('Company post code'), _('Company city'), _('Company subdivision'), _('Company country'), _('Company website'), _('Company NIP'), _('Company REGON'), _('Company KRS'), _('Tags')] %>
    ${button.dropdown_download_cols(request.route_url('user_export_companies_stars', username=user.name, _query=q), _export_cols)}
  </div>
</h2>
<hr>

<div id="map"></div>

<%include file="markers.mako"/>