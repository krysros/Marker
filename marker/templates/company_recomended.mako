<%inherit file="layout.mako"/>

<p class="lead">Firmę <a href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">${company.name}</a> rekomendują</p>
<%include file="user_table.mako"/>