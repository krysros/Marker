<%def name="add(route_name, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor':
<a class="btn btn-success" role="button" href="#" hx-get="${request.route_url(route_name, **kwargs)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Dodaj</a>
% else:
<button type="button" class="btn btn-success" disabled>Dodaj</button>
% endif
</%def>

<%def name="search(route_name, **kwargs)">
<a class="btn btn-primary" role="button" href="#" hx-get="${request.route_url(route_name, **kwargs)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Szukaj</a>
</%def>

<%def name="show(route_name, **kwargs)">
<a class="btn btn-secondary" role="button" href="#" hx-get="${request.route_url(route_name, **kwargs)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Pokaż</a>
</%def>

<%def name="edit(route_name, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor':
<a class="btn btn-warning" role="button" href="#" hx-get="${request.route_url(route_name, **kwargs)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Edytuj</a>
% else:
<button type="button" class="btn btn-warning" disabled>Edytuj</button>
% endif
</%def>

<%def name="danger(route_name, title, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor':
<button type="button" class="btn btn-danger" hx-post="${request.route_url(route_name, **kwargs)}" hx-confirm="Czy jesteś pewny?" hx-target="#main-container" hx-swap="innerHTML">
  ${title}
</button>
% else:
<button type="button" class="btn btn-danger" disabled>${title}</button>
% endif
</%def>

<%def name="del_card(route_name, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor':
<button class="btn btn-danger btn-sm" hx-post="${request.route_url(route_name, **kwargs)}" hx-confirm="Czy jesteś pewny?" hx-target="closest .card" hx-swap="outerHTML swap:1s">Usuń</button>
% else:
<button type="button" class="btn btn-danger btn-sm" disabled>Usuń</button>
% endif
</%def>

<%def name="del_row(route_name, **kwargs)">
% if request.is_authenticated and request.identity.role == 'editor':
<button class="btn btn-danger btn-sm" hx-post="${request.route_url(route_name, **kwargs)}" hx-confirm="Czy jesteś pewny?" hx-target="closest tr" hx-swap="outerHTML swap:1s">Usuń</button>
% else:
<button type="button" class="btn btn-danger btn-sm" disabled>Usuń</button>
% endif
</%def>