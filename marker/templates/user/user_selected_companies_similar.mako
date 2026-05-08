<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-intersect"></i> ${_("Similar companies")}
    <span class="badge bg-secondary">${counter}</span>
  </h2>
</div>
<hr>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <%include file="company_filter.mako"/>
  <div class="vr mx-1"></div>
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
  <div class="vr mx-1"></div>
  <a class="btn btn-sm btn-secondary active" aria-pressed="true" href="${request.route_url('user_selected_companies', username=user.name)}"><i class="bi bi-intersect"></i> ${_("Similar")}</a>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('Tag mode')}">
    <a class="btn ${'btn-primary' if tag_operator == 'or' else 'btn-outline-primary'}"
       href="${request.route_url('user_selected_companies_similar', username=user.name, _query={**{k: v for k, v in q.items() if k != 'tag_operator'}, 'tag_operator': 'or'})}">OR</a>
    <a class="btn ${'btn-primary' if tag_operator == 'and' else 'btn-outline-primary'}"
       href="${request.route_url('user_selected_companies_similar', username=user.name, _query={**{k: v for k, v in q.items() if k != 'tag_operator'}, 'tag_operator': 'and'})}">AND</a>
  </div>
  <div class="vr mx-1"></div>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-primary" href="${request.route_url('user_selected_companies_similar', username=user.name, _query=q)}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_map_selected_companies_similar', username=user.name, _query=q)}"><i class="bi bi-map"></i> ${_("Map")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_uptime_selected_companies_similar', username=user.name, _query={'tag_operator': tag_operator})}"><i class="bi bi-globe"></i> ${_("Uptime")}</a>
  </div>
</div>

<%include file="company_table.mako"/>
