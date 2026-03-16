<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-briefcase"></i> ${_("Projects")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a(icon='map', color='secondary', url=request.route_url('project_map', _query=q))}
    ${button.a(icon='search', color='primary', url=request.route_url('project_search'))}
    ${button.a(icon='plus-lg', color='success', url=request.route_url('project_add'))}
  </div>
</h2>

<hr>

<div class="hstack gap-2 mb-4 d-flex flex-wrap ">
  <%include file="project_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
  % if show_contacts_toggle:
  <div class="btn-group ms-auto" role="group" aria-label="${_('View mode')}">
    <a class="btn ${'btn-primary' if view_mode == 'projects' else 'btn-outline-primary'}" href="${request.current_route_url(_query={**q, 'view': 'projects'})}">
      ${_("Projects")}
    </a>
    <a class="btn ${'btn-primary' if view_mode == 'contacts' else 'btn-outline-primary'}" href="${request.current_route_url(_query={**q, 'view': 'contacts'})}">
      ${_("Contacts")}
    </a>
  </div>
  % endif
</div>

<%include file="search_criteria.mako"/>

% if view_mode == "contacts":
  <%include file="contact/contact_table.mako" args="q=contact_q"/>
% else:
  <%include file="project_table.mako"/>
% endif