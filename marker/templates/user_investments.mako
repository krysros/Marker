<%inherit file="layout.mako"/>

<p class="lead">Inwestycje dodane przez użytkownika <a href="${request.route_url('user_view', username=user.username)}">${user.fullname}</a></p>
<%include file="investment_table.mako"/>