<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-person-x"></i> ${_("Unassigned contacts")}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a(icon='search', color='primary', url=request.route_url('contact_search'))}
    ${button.a(icon='upload', color='success', url=request.route_url('contact_import_csv'))}
    ${button.a(icon='person-vcard', color='success', url=request.route_url('contact_import_vcard'))}
  </div>
</h2>

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
