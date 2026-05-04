<%inherit file="layout.mako"/>
<%namespace name="pills" file="pills.mako"/>
<%namespace name="button" file="button.mako" />

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div class="me-auto">${pills.pills(user_pills, active_url=request.route_url('user_comments', username=user.name))}</div>
</div>

<p class="lead">${user.fullname}</p>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <%include file="comment_filter.mako"/>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="search_criteria.mako"/>

<%def name="rows()">
% for comment in paginator:
% if loop.last:
<div hx-get="${next_page}"
     hx-trigger="revealed"
     hx-swap="afterend">
% else:
<div>
% endif
<%include file="comment_card.mako" args="comment=comment"/>
</div>
% endfor
</%def>

${rows()}