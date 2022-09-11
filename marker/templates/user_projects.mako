<%include file="navbar.mako"/>

<p class="lead">Projekty dodane przez użytkownika <a href="#" hx-get="${request.route_url('user_view', username=user.name)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">${user.fullname}</a></p>
<%include file="project_table.mako"/>