<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="user_pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(user_pills)}</div>
</div>

<p class="lead">${user.fullname}</p>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown(dd_filter)}</div>
  <div>${button.dropdown(dd_sort)}</div>
  <div>${button.dropdown(dd_order)}</div>
</div>

<%include file="company_table.mako"/>