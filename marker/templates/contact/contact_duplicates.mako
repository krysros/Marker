<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <div class="me-auto">${pills.pills(contact_pills, active_url=request.route_url('contact_duplicates', contact_id=contact.id, slug=contact.slug))}</div>
</div>

<%include file="contact_lead.mako"/>

<div class="d-flex flex-wrap align-items-center gap-2 mb-4 pb-1">
  <%include file="contact_filter.mako"/>
  ${button.dropdown_filter('category', _("Category"), categories)}
  <div class="vr mx-1"></div>
  ${button.dropdown_sort(sort_criteria)}
  ${button.dropdown_order(order_criteria)}
</div>

<%include file="search_criteria.mako"/>

<%include file="contact_table.mako"/>
