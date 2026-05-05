<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>
<%
  _contact_cols = [_('Contact name'), _('Contact role'), _('Contact phone'), _('Contact email')]
  _export_cols = _contact_cols + [_('Company name'), _('Company street'), _('Company post code'), _('Company city'), _('Company subdivision'), _('Company country'), _('Company website'), _('Company NIP'), _('Company REGON'), _('Company KRS'), _('Tags')]
%>
<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div class="me-auto">${pills.pills(user_pills, active_url=request.route_url('user_companies', username=user.name))}</div>
  <div>${button.dropdown_download_cols(request.route_url('user_export_companies', username=user.name, _query=q), _export_cols)}</div>
  <div>${button.a(icon='map', color='secondary', url=request.route_url('user_map_companies', username=user.name))}</div>
</div>

<p class="lead">${user.fullname}</p>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <%include file="company_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="company_table.mako"/>