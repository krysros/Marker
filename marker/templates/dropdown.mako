<%def name="filter_button(route_name, items, filter=None, sort=None, order=None, **kwargs)">
<div class="btn-group">
  <div class="dropdown">
    <a class="btn btn-secondary dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
      <i class="bi bi-filter"></i> Filtruj
    </a>
    <ul class="dropdown-menu">
      % for k, v in items.items():
      <li>
        <a class="dropdown-item" role="button" hx-get="${request.route_url(route_name, **kwargs, _query={'filter': k, 'sort': sort, 'order': order})}" hx-target="#main-container" hx-swap="innerHTML show:window:top">
          % if k == filter:
          <strong>${v}</strong>
          % else:
          ${v}
          % endif
        </a>
      </li>
      % else:
      <li>
        <a class="dropdown-item" role="button" hx-get="${request.route_url(route_name, **kwargs, _query={'filter': 'all', 'sort': sort, 'order': order})}" hx-target="#main-container" hx-swap="innerHTML show:window:top">
          % if filter == 'all':
          <strong>wszystkie</strong>
          % else:
          wszystkie
          % endif
        </a>
      </li>
      % endfor
    </ul>
  </div>
</div>
</%def>

<%def name="sort_button(route_name, items, filter=None, sort=None, order=None, **kwargs)">
<div class="btn-group">
  <div class="dropdown">
    <a class="btn btn-secondary dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
      Sortuj
    </a>
    <ul class="dropdown-menu">
      % for k, v in items.items():
      <li>
        <a class="dropdown-item" role="button" hx-get="${request.route_url(route_name, **kwargs, _query={'filter': filter, 'sort': k, 'order': order})}" hx-target="#main-container" hx-swap="innerHTML show:window:top">
          % if k == sort:
          <strong>${v}</strong>
          % else:
          ${v}
          % endif
        </a>
      </li>
      % endfor
    </ul>
  </div>
</div>
</%def>

<%def name="order_button(route_name, items, filter=None, sort=None, order=None, **kwargs)">
<div class="btn-group">
  <div class="dropdown">
    <a class="btn btn-secondary dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
      Kolejność
    </a>
    <ul class="dropdown-menu">
      % for k, v in items.items():
      <li>
        <a class="dropdown-item" role="button" hx-get="${request.route_url(route_name, **kwargs, _query={'filter': filter, 'sort': sort, 'order': k})}" hx-target="#main-container" hx-swap="innerHTML show:window:top">
          % if k == order:
          <strong>${v}</strong>
          % else:
          ${v}
          % endif
        </a>
      </li>
      % endfor
    </ul>
  </div>
</div>
</%def>