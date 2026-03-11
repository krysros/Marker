<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<h2>
  <i class="bi bi-people"></i> ${heading}
  <span class="badge bg-secondary">${counter}</span>
  <div class="float-end">
    ${button.a(icon=switch_icon, color='secondary', url=switch_url)}
  </div>
</h2>
<hr>

<div class="hstack gap-2 mb-4">
  <%include file="contact_filter.mako"/>
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div class="me-auto">${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="contact_table.mako"/>
