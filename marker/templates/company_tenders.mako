<%inherit file="layout.mako"/>

<p class="lead">Przetargi ogłoszone przez firmę <a href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">${company.name}</a></p>
<%include file="tender_table.mako"/>