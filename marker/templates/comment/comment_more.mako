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