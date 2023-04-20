<%inherit file="layout.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(user_pills)}</div>
</div>

<p class="lead">${user.fullname}</p>

<%include file="comment_more.mako"/>