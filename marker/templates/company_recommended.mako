<%inherit file="layout.mako"/>
<%namespace name="nav_pills" file="nav_pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${nav_pills.nav_company(company, active_link="recommended")}</div>
</div>

<%include file="company_lead.mako"/>
<%include file="user_table.mako"/>
