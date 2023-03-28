<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>
<%namespace name="pills" file="pills.mako"/>

<div class="hstack gap-2 mb-4">
  <div class="me-auto">${pills.company_pill(company)}</div>
</div>

<%include file="company_lead.mako"/>

<div class="hstack gap-2 mb-4">
  <div>${button.dropdown('company_similar', dd_filter, company_id=company.id, slug=company.slug)}</div>
</div>

<%include file="company_table.mako"/>