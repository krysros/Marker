<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-star"></i> ${_("Stars")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a(icon='table', color='secondary', url=request.route_url('user_projects_stars', username=user.name))}
    ${button.button(icon='star', color='warning', url=request.route_url('user_clear_projects_stars', username=user.name))}
    <% _contact_cols = [_('Contact name'), _('Contact role'), _('Contact phone'), _('Contact email')]; _export_cols = _contact_cols + [_('Project name'), _('Project street'), _('Project post code'), _('Project city'), _('Project subdivision'), _('Project country'), _('Project website'), _('Project deadline'), _('Project stage'), _('Project delivery method'), _('Project object category'), _('Tags')] %>
    ${button.dropdown_download_cols(request.route_url('user_export_projects_stars', username=user.name, _query=q), _export_cols)}
  </div>
</h2>
<hr>

<div id="map"></div>

<%include file="markers.mako"/>