<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<%
  _contact_cols = [_('Contact name'), _('Contact role'), _('Contact phone'), _('Contact email')]
  _company_cols = _contact_cols + [_('Company name'), _('Company street'), _('Company post code'), _('Company city'), _('Company subdivision'), _('Company country'), _('Company website'), _('Company NIP'), _('Company REGON'), _('Company KRS'), _('Tags')]
  _project_cols = _contact_cols + [_('Project name'), _('Project street'), _('Project post code'), _('Project city'), _('Project subdivision'), _('Project country'), _('Project website'), _('Project deadline'), _('Project stage'), _('Project delivery method'), _('Project object category'), _('Tags')]
  _export_cols = _project_cols if q.get('category') == 'projects' else _company_cols
%>
<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div class="me-auto">${pills.pills(user_pills, active_url=request.route_url('user_contacts', username=user.name))}</div>
  <div>${button.dropdown_download_cols(request.route_url('user_export_contacts', username=user.name, _query=q), _export_cols)}</div>
</div>

<p class="lead">${user.fullname}</p>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <%include file="contact_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="contact_table.mako"/>