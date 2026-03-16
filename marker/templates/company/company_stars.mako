<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4 d-flex flex-wrap ">
  <div class="me-auto">${pills.pills(company_pills)}</div>
  <div>${button.company_star(company)}</div>
</div>

<%include file="company_lead.mako"/>

<div class="hstack gap-2 mb-4 d-flex flex-wrap ">
  <div>${button.dropdown_sort(sort_criteria)}</div>
  <div>${button.dropdown_order(order_criteria)}</div>
</div>

<%include file="user_table.mako"/>
