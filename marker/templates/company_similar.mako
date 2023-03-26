<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="nav_pills" file="nav_pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${nav_pills.nav_company(company, active_link="similar")}</div>
</div>

<%include file="company_lead.mako"/>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('company_similar', dd_filter, company_id=company.id, slug=company.slug)}</div>
</div>

<%include file="company_table.mako"/>