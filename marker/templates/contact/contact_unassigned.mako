<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
  <h2 class="mb-0 text-nowrap flex-grow-1 flex-shrink-1">
    <i class="bi bi-person-x"></i> ${_("Unassigned contacts")}
    <span class="badge bg-secondary">${counter}</span>
  </h2>
  <div class="d-flex flex-wrap gap-2 justify-content-md-end w-100 w-md-auto">
    ${button.a(icon='search', color='primary', url=request.route_url('contact_search'))}
    ${button.dropdown_import(url_csv=request.route_url('contact_import_csv'), url_vcard=request.route_url('contact_import_vcard'))}
  </div>
</div>

<hr>

<div class="hstack gap-2 mb-4 d-flex flex-wrap">
  <%include file="contact_unassigned_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
  <div class="ms-auto">
    <div class="btn-group btn-group-sm" role="group">
      <a class="btn btn-outline-primary btn-sm" href="${request.route_url('contact_all')}"><i class="bi bi-people"></i> ${_("All")}</a>
      <a class="btn btn-primary btn-sm" href="${request.route_url('contact_unassigned')}"><i class="bi bi-person-x"></i> ${_("Unassigned")}</a>
    </div>
  </div>
</div>

<%
  q["category"] = ""
%>

<%include file="contact_table.mako"/>
