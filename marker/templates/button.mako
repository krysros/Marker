<%def name="edit(route_name, **kwargs)">
% if request.identity.role == 'editor':
<a class="btn btn-warning" role="button" href="#" hx-get="${request.route_url(route_name, **kwargs)}" hx-target="#main-container" hx-swap="innerHTML show:window:top">Edytuj</a>
% else:
<button type="button" class="btn btn-warning" disabled>Edytuj</button>
% endif
</%def>