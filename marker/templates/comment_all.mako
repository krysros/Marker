<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-chat-left-text"></i> Komentarze
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.search('comment_search')}
  </div>
</h2>

<hr>

<%include file="comment_more.mako"/>