<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-briefcase"></i> ${_("Projects")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a(icon='search', color='primary', url=request.route_url('project_search'))}
    ${button.a(icon='plus-lg', color='success', url=request.route_url('project_add'))}
    % if gemini_api_key_set:
    ${button.a(icon='robot', color='success', url=request.route_url('project_add_ai'))}
    % endif
  </div>
</h2>

<hr>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <%include file="project_filter.mako"/>
  <div class="vr mx-1"></div>
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
  % if show_contacts_toggle:
  <div class="vr mx-1"></div>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}">
    <a class="btn ${'btn-primary' if view_mode == 'projects' else 'btn-outline-primary'}" href="${request.current_route_url(_query={**q, 'view': 'projects'})}">
      <i class="bi bi-briefcase"></i> ${_("Projects")}
    </a>
    <a class="btn ${'btn-primary' if view_mode == 'contacts' else 'btn-outline-primary'}" href="${request.current_route_url(_query={**q, 'view': 'contacts'})}">
      <i class="bi bi-people"></i> ${_("Contacts")}
    </a>
  </div>
  % endif
  <div class="vr mx-1"></div>
  <div class="btn-group btn-group-sm" role="group" aria-label="${_('View mode')}">
    <a class="btn btn-primary" href="${request.route_url('project_all', _query=q)}"><i class="bi bi-table"></i> ${_("Table")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('project_map', _query=q)}"><i class="bi bi-map"></i> ${_("Map")}</a>
    <a class="btn btn-outline-primary" href="${request.route_url('project_uptime')}"><i class="bi bi-globe"></i> ${_("Uptime")}</a>
  </div>
</div>

<%include file="search_criteria.mako"/>

% if view_mode == "contacts":
  <%include file="contact/contact_table.mako" args="q=contact_q"/>
% else:
  <%include file="project_table.mako"/>
% endif