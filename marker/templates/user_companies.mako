<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="nav_pills" file="nav_pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${nav_pills.user_pill(user)}</div>
</div>

<p class="lead">${user.fullname}</p>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('user_companies', dd_filter, username=user.name)}</div>
  <div>${button.dropdown('user_companies', dd_sort, username=user.name)}</div>
  <div>${button.dropdown('user_companies', dd_order, username=user.name)}</div>
</div>

<%include file="company_table.mako"/>