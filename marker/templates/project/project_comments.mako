<%inherit file="layout.mako"/>
<%namespace name="pills" file="pills.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <div class="me-auto">${pills.pills(project_pills)}</div>
% if request.identity.role == 'editor' or 'admin':
  <a href="${request.route_url('project_add_comment', project_id=project.id, slug=project.slug)}" class="btn btn-success"><i class="bi bi-plus-lg"></i></a>
% else:
  <button type="button" class="btn btn-success" disabled><i class="bi bi-plus-lg"></i></button>
% endif
</div>

<%include file="project_lead.mako"/>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
</div>

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
