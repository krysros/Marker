<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-body">
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" id="filterUsers" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        <i class="fa fa-filter" aria-hidden="true"></i> Filtruj
      </button>
      <div class="dropdown-menu" aria-labelledby="filterUsers">
        <a class="dropdown-item" href="${request.route_url('user_all', _query={'filter': 'basic', 'sort': sort})}">
          % if filter == 'basic':
          <strong>Wyświetlanie</strong>
          % else:
          Wyświetlanie
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('user_all', _query={'filter': 'editor', 'sort': sort})}">
          % if filter == 'editor':  
          <strong>Edytowanie</strong>
          % else:
          Edytowanie
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('user_all', _query={'filter': 'admin', 'sort': sort})}">
          % if filter == 'admin':
          <strong>Administrator</strong>
          % else:
          Administrator
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('user_all', _query={'filter': 'all', 'sort': sort})}">
          % if filter == 'all':
          <strong>Wszystkie</strong>
          % else:
          Wszystkie
          % endif
        </a>
      </div>
    </div>
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" id="sortUsers" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Sortuj
      </button>
      <div class="dropdown-menu" aria-labelledby="sortUsers">
        <a class="dropdown-item" href="${request.route_url('user_all', _query={'filter': filter, 'sort': 'username'})}">
          % if sort == 'username':
          <strong>wg nazwy</strong>
          % else:
          wg nazwy
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('user_all', _query={'filter': filter, 'sort': 'added'})}">
          % if sort == 'added':
          <strong>wg daty dodania</strong>
          % else:
          wg daty dodania
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('user_all', _query={'filter': filter, 'sort': 'edited'})}">
          % if sort == 'edited':
          <strong>wg daty edycji</strong>
          % else:
          wg daty edycji
          % endif
        </a>
      </div>
    </div>
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" id="orderUsers" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Kolejność
      </button>
      <div class="dropdown-menu" aria-labelledby="orderUsers">
        <a class="dropdown-item" href="${request.route_url('user_all', _query={'filter': filter, 'sort': sort, 'order': 'asc'})}">
          % if order == 'asc':
          <strong>rosnąco</strong>
          % else:
          rosnąco
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('user_all', _query={'filter': filter, 'sort': sort, 'order': 'desc'})}">
          % if order == 'desc':
          <strong>malejąco</strong>
          % else:
          malejąco
          % endif
        </a>
      </div>
    </div>
  </div>
</div>

<%include file="user_table.mako"/>