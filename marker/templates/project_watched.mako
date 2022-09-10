<%include file="navbar.mako"/>

<p class="lead">Projekt <a href="#top" hx-get="${request.route_url('project_view', project_id=project.id, slug=project.slug)}" hx-target="#main-container">${project.name}</a> obserwują</p>
<%include file="user_table.mako"/>