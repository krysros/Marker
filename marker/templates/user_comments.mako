<%inherit file="layout.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(user_pills, active_url=request.route_url('user_comments', username=user.name))}</div>
</div>

<p class="lead">${user.fullname}</p>

<%include file="comment_more.mako"/>