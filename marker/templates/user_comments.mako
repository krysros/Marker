<%inherit file="layout.mako"/>
<%namespace name="nav_pills" file="nav_pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${nav_pills.user_pill(user)}</div>
</div>

<p class="lead">${user.fullname}</p>

<%include file="comment_more.mako"/>