<%inherit file="layout.mako" />
<%namespace name="button" file="button.mako" />

<h2>
  <i class="bi bi-chat-left-text"></i> ${_("Comments")}
  <span class="badge bg-secondary"><div hx-get="${request.route_url('comment_count')}" hx-trigger="commentEvent from:body">${counter}</div></span>
  <div class="float-end">
    ${button.a_btn(icon='search', color='primary', url=request.route_url('comment_search'))}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown(dd_filter, search_query)}</div>
  <div>${button.dropdown(dd_order, search_query)}</div>
</div>

% if any(x for x in form.data.values() if x):
<div class="alert alert-info" role="alert">
  <strong>Kryteria wyszukiwania: </strong>
  % for k, v in form.data.items():
    % if v:
      ${form[k].label.text}: <strong>${v}</strong>; 
    % endif
  % endfor
</div>
% endif

<%include file="comment_more.mako" />