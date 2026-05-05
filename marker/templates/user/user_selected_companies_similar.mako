<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-intersect"></i> ${_("Similar companies")}
    <span class="badge bg-secondary">${counter}</span>
  </h2>
</div>
<hr>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <%include file="company_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
  <a class="btn btn-secondary active" aria-pressed="true" href="${request.route_url('user_selected_companies', username=user.name)}"><i class="bi bi-intersect"></i> ${_("Similar")}</a>
  <div class="btn-group" role="group" aria-label="${_('Tag mode')}">
    <a class="btn ${'btn-primary' if tag_operator == 'or' else 'btn-outline-primary'}"
       href="${request.route_url('user_selected_companies_similar', username=user.name, _query={**{k: v for k, v in q.items() if k != 'tag_operator'}, 'tag_operator': 'or'})}">OR</a>
    <a class="btn ${'btn-primary' if tag_operator == 'and' else 'btn-outline-primary'}"
       href="${request.route_url('user_selected_companies_similar', username=user.name, _query={**{k: v for k, v in q.items() if k != 'tag_operator'}, 'tag_operator': 'and'})}">AND</a>
  </div>
  <div class="btn-group ms-auto" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_tags', username=user.name)}">${_("Tags")}</a>
    <a class="btn btn-primary" href="${request.route_url('user_selected_companies', username=user.name)}">${_("Companies")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_projects', username=user.name)}">${_("Projects")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('user_selected_contacts', username=user.name)}">${_("Contacts")}</a>
  </div>
</div>

<%include file="company_table.mako"/>
