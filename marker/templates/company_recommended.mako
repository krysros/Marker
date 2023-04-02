<%inherit file="layout.mako"/>
<%namespace name="pills" file="company_pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.pills(company)}</div>
</div>

<%include file="company_lead.mako"/>
<%include file="user_table.mako"/>
