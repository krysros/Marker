<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-body">
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" id="filterCategory" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Kategoria
      </button>
      <div class="dropdown-menu" aria-labelledby="filterCategory">
        <a class="dropdown-item" href="${request.route_url('company_all', _query={'filter': 'default', 'sort': sort})}">
          % if filter == 'default':
          <strong>domyślna</strong>
          % else:
          domyślna
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('company_all', _query={'filter': 'success', 'sort': sort})}">
          % if filter == 'success':
          <strong>zielona</strong>
          % else:
          zielona
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('company_all', _query={'filter': 'info', 'sort': sort})}">
          % if filter == 'info':
          <strong>niebieska</strong>
          % else:
          niebieska
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('company_all', _query={'filter': 'warning', 'sort': sort})}">
          % if filter == 'warning':
          <strong>pomarańczowa</strong>
          % else:
          pomarańczowa
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('company_all', _query={'filter': 'danger', 'sort': sort})}">
          % if filter == 'danger':  
          <strong>czerwona</strong>
          % else:
          czerwona
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('company_all', _query={'filter': 'all', 'sort': sort})}">
          % if filter == 'all':
          <strong>wszystkie</strong>
          % else:
          wszystkie
          % endif
        </a>
      </div>
    </div>
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" id="sortCompanies" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Sortuj
      </button>
      <div class="dropdown-menu" aria-labelledby="sortCompanies">
        <a class="dropdown-item" href="${request.route_url('company_all', _query={'filter': filter, 'sort': 'name'})}">
          % if sort == 'name':
          <strong>wg nazwy</strong>
          % else:
          wg nazwy
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('company_all', _query={'filter': filter, 'sort': 'created_at'})}">
          % if sort == 'created_at':
          <strong>wg daty dodania</strong>
          % else:
          wg daty dodania
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('company_all', _query={'filter': filter, 'sort': 'updated_at'})}">
          % if sort == 'updated_at':
          <strong>wg daty edycji</strong>
          % else:
          wg daty edycji
          % endif
        </a>
      </div>
    </div>
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" id="orderCompanies" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Kolejność
      </button>
      <div class="dropdown-menu" aria-labelledby="orderCompanies">
        <a class="dropdown-item" href="${request.route_url('company_all', _query={'filter': filter, 'sort': sort, 'order': 'asc'})}">
          % if order == 'asc':
          <strong>rosnąco</strong>
          % else:
          rosnąco
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('company_all', _query={'filter': filter, 'sort': sort, 'order': 'desc'})}">
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

<%include file="company_table.mako"/>