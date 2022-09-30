<%def name="show(route_name, **kwargs)">
<a class="btn btn-secondary btn-sm" role="button" href="${request.route_url(route_name, **kwargs)}">Pokaż</a>
</%def>

<%def name="search(route_name, **kwargs)">
<a class="btn btn-primary btn-sm" role="button" href="${request.route_url(route_name, **kwargs)}">Szukaj</a>
</%def>

<%def name="export(route_name, **kwargs)">
<a class="btn btn-primary btn-sm" role="button" href="${request.route_url(route_name, **kwargs)}">Eksportuj</a>
</%def>

<%def name="add(route_name, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor':
<a class="btn btn-success btn-sm" role="button" href="${request.route_url(route_name, **kwargs)}">Dodaj</a>
% else:
<button type="button" class="btn btn-success btn-sm" disabled>Dodaj</button>
% endif
</%def>

<%def name="edit(route_name, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor':
<a class="btn btn-warning btn-sm" role="button" href="${request.route_url(route_name, **kwargs)}">Edytuj</a>
% else:
<button type="button" class="btn btn-warning btn-sm" disabled>Edytuj</button>
% endif
</%def>

<%def name="delete(route_name, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor':
<button type="button" class="btn btn-danger btn-sm" hx-post="${request.route_url(route_name, **kwargs)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-confirm="Czy jesteś pewny?">Usuń</button>
% else:
<button type="button" class="btn btn-danger btn-sm" disabled>${title}</button>
% endif
</%def>

<%def name="clear(route_name, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor':
<button type="button" class="btn btn-danger btn-sm" hx-post="${request.route_url(route_name, **kwargs)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-confirm="Czy jesteś pewny?">Wyczyść</button>
% else:
<button type="button" class="btn btn-danger btn-sm" disabled>${title}</button>
% endif
</%def>

<%def name="del_card(route_name, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor':
<button type="button" class="btn btn-danger btn-sm" hx-post="${request.route_url(route_name, **kwargs)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-confirm="Czy jesteś pewny?" hx-target="closest .card" hx-swap="outerHTML swap:1s">Usuń</button>
% else:
<button type="button" class="btn btn-danger btn-sm" disabled>Usuń</button>
% endif
</%def>

<%def name="del_row(route_name, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor':
<button type="button" class="btn btn-danger btn-sm" hx-post="${request.route_url(route_name, **kwargs)}" hx-headers='{"X-CSRF-Token": "${get_csrf_token()}"}' hx-confirm="Czy jesteś pewny?" hx-target="closest tr" hx-swap="outerHTML swap:1s">Usuń</button>
% else:
<button type="button" class="btn btn-danger btn-sm" disabled>Usuń</button>
% endif
</%def>