<%inherit file="layout.mako" />
<%namespace name="button" file="button.mako" />

<h2>
  <i class="bi bi-chat-left-text"></i> Komentarze
  <span class="badge bg-secondary"><div hx-get="${request.route_url('comment_count')}" hx-trigger="commentEvent from:body">${counter}</div></span>
  <div class="float-end">
    ${button.search('comment_search')}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('comment_all', dd_filter)}</div>
  <div>${button.dropdown('comment_all', dd_order)}</div>
</div>

% if form:
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