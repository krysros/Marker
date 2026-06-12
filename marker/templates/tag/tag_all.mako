<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-tags"></i> ${_("Tags")}
  <span class="badge bg-secondary">
    <div hx-get="${request.route_url('tag_count')}" hx-trigger="tagEvent from:body">${counter}</div>
  </span>
  <div class="float-end">
    ${button.a(icon='stars', color='info', url=request.route_url('tag_search_ai'), title=_("AI Search"))}
    ${button.a(icon='search', color='primary', url=request.route_url('tag_search'))}
    ${button.a(icon='plus-lg', color='success', url=request.route_url('tag_add'))}
  </div>
</h2>
<hr>

<div id="main-container" hx-boost="true" hx-target="#main-container" hx-select="#main-container" hx-swap="outerHTML" hx-push-url="true">
<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <%include file="tag_filter.mako"/>
  <div class="vr mx-1"></div>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
  <div class="vr mx-1"></div>
  <%
    matched_route_name = getattr(request, "matched_route", None).name if getattr(request, "matched_route", None) else ""
    is_unassigned = matched_route_name == 'tag_unassigned'
    is_duplicates = matched_route_name == 'tag_duplicates_all'
    is_all = not is_unassigned and not is_duplicates
  %>
  ${button.dropdown_list_mode(
    all_url=request.route_url('tag_all', _query=q),
    unassigned_url=request.route_url('tag_unassigned', _query=q),
    duplicates_url=request.route_url('tag_duplicates_all', _query=q),
    is_all=is_all,
    is_unassigned=is_unassigned,
    is_duplicates=is_duplicates,
    icon_all='tags',
    icon_unassigned='tag-x'
  )}
</div>

<%include file="search_criteria.mako"/>

<%include file="tag_table.mako"/>
</div>