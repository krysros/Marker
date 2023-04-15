<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="user_pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(user)}</div>
</div>

<p class="lead">${user.fullname}</p>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown(dd_sort, search_query)}</div>
  <div>${button.dropdown(dd_order, search_query)}</div>
</div>

<%include file="tag_table.mako"/>