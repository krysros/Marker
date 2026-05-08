<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-people"></i> ${_("Contacts")}
    <span class="badge bg-secondary"><div hx-get="${request.route_url('contact_count')}" hx-trigger="contactEvent from:body">${counter}</div></span>
  </h2>
  <div class="d-flex flex-wrap gap-2 justify-content-md-end w-100 w-md-auto">
    ${button.a(icon='search', color='primary', url=request.route_url('contact_search'))}
    ${button.dropdown_import(url_csv=request.route_url('contact_import_csv'), url_vcard=request.route_url('contact_import_vcard'))}
  </div>
</div>

<hr>

<div class="d-flex flex-nowrap overflow-x-auto align-items-center gap-2 mb-4 pb-1">
  <%include file="contact_filter.mako"/>
  <div class="vr mx-1"></div>
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
  <div class="vr mx-1"></div>
  <div class="btn-group btn-group-sm" role="group">
    <a class="btn btn-primary btn-sm" href="${request.route_url('contact_all')}"><i class="bi bi-people"></i> ${_("All")}</a>
    <a class="btn btn-outline-primary btn-sm" href="${request.route_url('contact_unassigned')}"><i class="bi bi-person-x"></i> ${_("Unassigned")}</a>
  </div>
</div>

<%include file="search_criteria.mako"/>

<%include file="contact_table.mako"/>