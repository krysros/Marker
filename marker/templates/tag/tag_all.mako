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
  <div class="btn-group btn-group-sm" role="group">
    <a class="btn ${'btn-primary' if q.get('duplicates') != '1' else 'btn-outline-primary'} btn-sm" href="${request.route_url('tag_all', _query={**q, 'duplicates': None})}"><i class="bi bi-tags"></i> ${_("All")}</a>
    <a class="btn btn-outline-primary btn-sm" href="${request.route_url('tag_unassigned')}"><i class="bi bi-tag-x"></i> ${_("Unassigned")}</a>
    <a class="btn ${'btn-primary' if q.get('duplicates') == '1' else 'btn-outline-primary'} btn-sm" href="${request.route_url('tag_all', _query={**q, 'duplicates': '1'})}"><i class="bi bi-files"></i> ${_("Duplicates")}</a>
  </div>
</div>

<%include file="search_criteria.mako"/>

<%include file="tag_table.mako"/>
</div>