<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="nav_pills" file="nav_pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${nav_pills.user_pill(user)}</div>
</div>

<p class="lead">${user.fullname}</p>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('user_contacts', dd_sort, username=user.name)}</div>
  <div>${button.dropdown('user_contacts', dd_order, username=user.name)}</div>
</div>

<%include file="contact_table.mako"/>