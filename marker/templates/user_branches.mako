<%inherit file="layout.mako"/>

<p class="lead">Branże dodane przez użytkownika <a href="${request.route_url('user_view', username=user.username)}">${user.fullname}</a></p>
<%include file="branch_table.mako"/>