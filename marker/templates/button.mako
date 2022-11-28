<%def name="show(route_name, **kwargs)">
<a class="btn btn-secondary" role="button" href="${request.route_url(route_name, **kwargs)}"><i class="bi bi-folder"></i></a>
</%def>

<%def name="search(route_name, **kwargs)">
<a class="btn btn-primary" role="button" href="${request.route_url(route_name, **kwargs)}"><i class="bi bi-search"></i></a>
</%def>

<%def name="export(route_name, **kwargs)">
<a class="btn btn-primary" role="button" href="${request.route_url(route_name, **kwargs)}"><i class="bi bi-download"></i></a>
</%def>

<%def name="table(route_name, **kwargs)">
<a class="btn btn-secondary" role="button" href="${request.route_url(route_name, **kwargs)}"><i class="bi bi-table"></i></a>
</%def>

<%def name="map(route_name, **kwargs)">
<a class="btn btn-secondary" role="button" href="${request.route_url(route_name, **kwargs)}"><i class="bi bi-map"></i></a>
</%def>

<%def name="add(route_name, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor':
<a class="btn btn-success" role="button" href="${request.route_url(route_name, **kwargs)}"><i class="bi bi-plus-lg"></i></a>
% else:
<button type="button" class="btn btn-success" disabled><i class="bi bi-plus-lg"></i></button>
% endif
</%def>

<%def name="edit(route_name, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor':
<a class="btn btn-warning" role="button" href="${request.route_url(route_name, **kwargs)}"><i class="bi bi-pencil-square"></i></a>
% else:
<button type="button" class="btn btn-warning" disabled><i class="bi bi-pencil-square"></i></button>
% endif
</%def>

<%def name="delete(route_name, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor':
<button type="button" class="btn btn-danger" hx-post="${request.route_url(route_name, **kwargs)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-confirm="Czy jesteś pewny?"><i class="bi bi-trash"></i></button>
% else:
<button type="button" class="btn btn-danger" disabled><i class="bi bi-trash"></i></button>
% endif
</%def>

<%def name="clear(route_name, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor':
<button type="button" class="btn btn-danger" hx-post="${request.route_url(route_name, **kwargs)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-confirm="Czy jesteś pewny?"><i class="bi bi-square"></i></button>
% else:
<button type="button" class="btn btn-danger" disabled><i class="bi bi-square"></i></button>
% endif
</%def>

<%def name="unlink(route_name, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor':
<button type="button" class="btn btn-warning btn-sm" hx-post="${request.route_url(route_name, **kwargs)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-confirm="Czy jesteś pewny?" hx-target="closest tr" hx-swap="outerHTML swap:1s"><i class="bi bi-dash-lg"></i></button>
% else:
<button type="button" class="btn btn-warning btn-sm" disabled><i class="bi bi-dash-lg"></i></button>
% endif
</%def>

<%def name="del_card(route_name, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor':
<button type="button" class="btn btn-danger btn-sm" hx-post="${request.route_url(route_name, **kwargs)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-confirm="Czy jesteś pewny?" hx-target="closest .card" hx-swap="outerHTML swap:1s"><i class="bi bi-trash"></i></button>
% else:
<button type="button" class="btn btn-danger btn-sm" disabled><i class="bi bi-trash"></i></button>
% endif
</%def>

<%def name="del_row(route_name, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor':
<button type="button" class="btn btn-danger btn-sm" hx-post="${request.route_url(route_name, **kwargs)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-confirm="Czy jesteś pewny?" hx-target="closest tr" hx-swap="outerHTML swap:1s"><i class="bi bi-trash"></i></button>
% else:
<button type="button" class="btn btn-danger btn-sm" disabled><i class="bi bi-trash"></i></button>
% endif
</%def>