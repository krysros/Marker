<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="user_pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(user)}</div>
</div>

<p class="lead">${user.fullname}</p>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown(dd_filter, url=request.route_url('user_companies', username=user.name))}</div>
  <div>${button.dropdown(dd_sort, url=request.route_url('user_companies', username=user.name))}</div>
  <div>${button.dropdown(dd_order, url=request.route_url('user_companies', username=user.name))}</div>
</div>

<%include file="company_table.mako"/>