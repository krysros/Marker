<%def name="edit(route_name, **kwargs)">
% if request.identity.role == 'editor':
<a class="btn btn-warning" role="button" href="#" hx-get="${request.route_url(route_name, **kwargs)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Edytuj</a>
% else:
<button type="button" class="btn btn-warning" disabled>Edytuj</button>
% endif
</%def>

<%def name="danger(route_name, title, body, **kwargs)">
% if request.identity.role == 'editor':
<button type="button" class="btn btn-danger" hx-post="${request.route_url(route_name, **kwargs)}" hx-confirm="Czy jesteś pewny?" hx-target="#main-container" hx-swap="innerHTML">
  ${title}
</button>
% else:
<button type="button" class="btn btn-danger" disabled>${title}</button>
% endif
</%def>