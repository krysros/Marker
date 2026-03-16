<%inherit file="layout.mako"/>
<%namespace name="pills" file="pills.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div class="me-auto">${pills.pills(project_pills)}</div>
  <div>
    % if request.identity.role == 'editor' or 'admin':
    ${button.a(icon='plus-lg', color='success', url=request.route_url('project_add_comment', project_id=project.id, slug=project.slug))}
    % else:
    <button type="button" class="btn btn-success" disabled><i class="bi bi-plus-lg"></i></button>
    % endif
  </div>
</div>

<%include file="project_lead.mako"/>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="comment_more.mako"/>
