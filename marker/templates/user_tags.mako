<%include file="navbar.mako"/>

<p class="lead">Tagi dodane przez użytkownika <a href="#top" hx-get="${request.route_url('user_view', username=user.name)}" hx-target="#main-container">${user.fullname}</a></p>
<%include file="tag_table.mako"/>