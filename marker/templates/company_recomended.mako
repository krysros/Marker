<%include file="navbar.mako"/>

<p class="lead">Firmę <a href="#" hx-get="${request.route_url('company_view', company_id=company.id, slug=company.slug)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">${company.name}</a> rekomendują</p>
<%include file="user_table.mako"/>