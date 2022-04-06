<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-body">
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" id="sortBranches" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Sortuj
      </button>
      <div class="dropdown-menu" aria-labelledby="sortBranches">
        <a class="dropdown-item" href="${request.route_url('branch_all', _query={'sort': 'name', 'order': order})}">
          % if sort == 'name':
          <strong>wg nazwy</strong>
          % else:
          wg nazwy
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('branch_all', _query={'sort': 'added', 'order': order})}">
          % if sort == 'added':
          <strong>wg daty dodania</strong>
          % else:
          wg daty dodania
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('branch_all', _query={'sort': 'edited', 'order': order})}">
          % if sort == 'edited':
          <strong>wg daty edycji</strong>
          % else:
          wg daty edycji
          % endif
        </a>
      </div>
    </div>
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" id="orderBranches" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Kolejność
      </button>
      <div class="dropdown-menu" aria-labelledby="orderBranches">
        <a class="dropdown-item" href="${request.route_url('branch_all', _query={'sort': sort, 'order': 'asc'})}">
          % if order == 'asc':
          <strong>rosnąco</strong>
          % else:
          rosnąco
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('branch_all', _query={'sort': sort, 'order': 'desc'})}">
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

<%include file="branch_table.mako"/>