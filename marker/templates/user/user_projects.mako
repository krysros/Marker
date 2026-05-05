<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>
<%
  _contact_cols = [_('Contact name'), _('Contact role'), _('Contact phone'), _('Contact email')]
  _export_cols = _contact_cols + [_('Project name'), _('Project street'), _('Project post code'), _('Project city'), _('Project subdivision'), _('Project country'), _('Project website'), _('Project deadline'), _('Project stage'), _('Project delivery method'), _('Project object category'), _('Tags')]
%>
<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div class="me-auto">${pills.pills(user_pills, active_url=request.route_url('user_projects', username=user.name))}</div>
  <div>${button.dropdown_download_cols(request.route_url('user_export_projects', username=user.name, _query=q), _export_cols)}</div>
  <div>${button.a(icon='map', color='secondary', url=request.route_url('user_map_projects', username=user.name))}</div>
</div>

<p class="lead">${user.fullname}</p>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <%include file="project_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="project_table.mako"/>