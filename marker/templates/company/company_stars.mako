<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(company_pills)}</div>
  <div>${button.company_star(company)}</div>
</div>

<%include file="company_lead.mako"/>
<%include file="user_table.mako"/>
