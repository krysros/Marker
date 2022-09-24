<%inherit file="layout.mako"/>

<p class="lead">Tagi dodane przez użytkownika <a href="${request.route_url('user_view', username=user.name)}">${user.fullname}</a></p>
<%include file="tag_table.mako"/>