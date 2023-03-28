<%inherit file="layout.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.company_pill(company)}</div>
</div>

<%include file="company_lead.mako"/>
<%include file="user_table.mako"/>
