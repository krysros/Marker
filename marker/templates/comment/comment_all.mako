<%inherit file="layout.mako" />
<%namespace name="button" file="button.mako" />

<h2>
  <i class="bi bi-chat-left-text"></i> ${_("Comments")}
  <span class="badge bg-secondary"><div hx-get="${request.route_url('comment_count')}" hx-trigger="commentEvent from:body">${counter}</div></span>
  <div class="float-end">
    ${button.a(icon='search', color='primary', url=request.route_url('comment_search'))}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <%include file="comment_filter.mako"/>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="comment_more.mako" />