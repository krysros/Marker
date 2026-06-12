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

<div id="main-container" hx-boost="true" hx-target="#main-container" hx-select="#main-container" hx-swap="outerHTML" hx-push-url="true">
<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <%include file="contact_unassigned_filter.mako"/>
  <div class="vr mx-1"></div>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
  <div class="vr mx-1"></div>
  <%
    matched_route_name = getattr(request, "matched_route", None).name if getattr(request, "matched_route", None) else ""
    is_unassigned = matched_route_name == 'contact_unassigned'
    is_duplicates = matched_route_name == 'contact_duplicates_all'
    is_all = not is_unassigned and not is_duplicates
  %>
  ${button.dropdown_list_mode(
    all_url=request.route_url('contact_all', _query=q),
    unassigned_url=request.route_url('contact_unassigned', _query=q),
    duplicates_url=request.route_url('contact_duplicates_all', _query=q),
    is_all=is_all,
    is_unassigned=is_unassigned,
    is_duplicates=is_duplicates,
    icon_all='people',
    icon_unassigned='person-x'
  )}
</div>

<%
  q["category"] = ""
%>

<%include file="contact_table.mako"/>
</div>
