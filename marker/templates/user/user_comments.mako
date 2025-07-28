<%inherit file="layout.mako"/>
<%namespace name="pills" file="pills.mako"/>
<%namespace name="button" file="button.mako" />

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(user_pills, active_url=request.route_url('user_comments', username=user.name))}</div>
</div>

<p class="lead">${user.fullname}</p>

<div class="hstack gap-2 mb-4">
  <%include file="comment_filter.mako"/>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="comment_more.mako"/>