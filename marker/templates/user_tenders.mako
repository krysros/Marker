<%inherit file="layout.mako"/>

<p class="lead">Przetargi dodane przez użytkownika <a href="${request.route_url('user_view', username=user.username)}">${user.fullname}</a></p>
<%include file="tender_table.mako"/>