<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(user_pills, active_url=request.route_url('user_tags', username=user.name))}</div>
</div>

<p class="lead">${user.fullname}</p>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown(dd_sort)}</div>
  <div>${button.dropdown(dd_order)}</div>
</div>

<%include file="tag_table.mako"/>