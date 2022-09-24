<%inherit file="layout.mako"/>

<p class="lead">Projekt <a href="${request.route_url('project_view', project_id=project.id, slug=project.slug)}">${project.name}</a> obserwują</p>
<%include file="user_table.mako"/>