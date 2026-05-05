<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<%! from marker.utils.export_columns import company_cols, project_cols %>
<% _export_cols = project_cols(_) if q.get('category') == 'projects' else company_cols(_) %>
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