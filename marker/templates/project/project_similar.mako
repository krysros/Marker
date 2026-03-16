<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4 d-flex flex-wrap ">
  <div class="me-auto">${pills.pills(project_pills, active_url=request.route_url('project_similar', project_id=project.id, slug=project.slug))}</div>
</div>

<%include file="project_lead.mako"/>

<div class="hstack gap-2 mb-4 d-flex flex-wrap ">
  <%include file="project_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="search_criteria.mako"/>

<%include file="project_table.mako"/>