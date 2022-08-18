<%inherit file="layout.mako"/>

<p class="lead">Projekty zrealizowane przez firmę <a href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">${company.name}</a></p>
<%include file="project_table.mako"/>