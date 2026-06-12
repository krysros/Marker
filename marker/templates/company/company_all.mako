<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-buildings"></i> ${_("Companies")}
  <span class="badge bg-secondary">
    <div hx-get="${request.route_url('company_count')}" hx-trigger="companyEvent from:body">${counter}</div>
  </span>
  <div class="float-end">
    ${button.a(icon='search', color='primary', url=request.route_url('company_search'))}
    ${button.a(icon='plus-lg', color='success', url=request.route_url('company_add'))}
    % if gemini_api_key_set:
    ${button.a(icon='stars', color='info', url=request.route_url('company_add_ai'), title=_("AI Add"))}
    % endif
  </div>
</h2>

<hr>

<div id="main-container" hx-boost="true" hx-target="#main-container" hx-select="#main-container" hx-swap="outerHTML" hx-push-url="true">
<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <%include file="company_filter.mako"/>
  <div class="vr mx-1"></div>
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
  % if show_contacts_toggle:
  <div class="vr mx-1"></div>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}">
    <a class="btn ${'btn-primary' if view_mode == 'companies' else 'btn-outline-primary'}" href="${request.current_route_url(_query={**q, 'view': 'companies'})}">
      <i class="bi bi-buildings"></i> ${_("Companies")}
    </a>
    <a class="btn ${'btn-primary' if view_mode == 'contacts' else 'btn-outline-primary'}" href="${request.current_route_url(_query={**q, 'view': 'contacts'})}">
      <i class="bi bi-people"></i> ${_("Contacts")}
    </a>
  </div>
  % endif
  <div class="vr mx-1"></div>
  <%
    matched_route_name = getattr(request, "matched_route", None).name if getattr(request, "matched_route", None) else ""
  %>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}" hx-boost="false">
    <a class="btn ${'btn-primary' if matched_route_name == 'company_all' else 'btn-outline-primary'}" href="${request.route_url('company_all', _query=q)}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('company_map', _query=q)}"><i class="bi bi-map"></i> ${_("Map")}</a>
  </div>
  <div class="vr mx-1"></div>
  ${button.dropdown_quality(
    uptime_url=request.route_url('company_uptime', _query=q),
    duplicates_url=request.route_url('company_duplicates_all', _query=q),
    nolocation_url=request.route_url('company_nolocation', _query=q),
    is_uptime=matched_route_name == 'company_uptime',
    is_duplicates=matched_route_name == 'company_duplicates_all',
    is_nolocation=matched_route_name == 'company_nolocation'
  )}
</div>

<%include file="search_criteria.mako"/>

% if view_mode == "contacts":
  <%include file="contact/contact_table.mako" args="q=contact_q"/>
% else:
  <%include file="company_table.mako"/>
% endif
</div>