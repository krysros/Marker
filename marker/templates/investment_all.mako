<%inherit file="layout.mako"/>

<form id="investment_export" action="${request.route_url('investment_export')}" method="post">
  <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
  <input type="hidden" name="filter" value=${filter}>
  <input type="hidden" name="sort" value=${sort}>
  <input type="hidden" name="order" value=${order}>
</form>

<div class="card">
  <div class="card-body">
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" id="filterInvestments" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        <i class="fa fa-filter" aria-hidden="true"></i> Filtruj
      </button>
      <div class="dropdown-menu" aria-labelledby="filterInvestments">
        <a class="dropdown-item" href="${request.route_url('investment_all', _query={'filter': 'inprogress', 'sort': sort, 'order': order})}">
          % if filter == 'inprogress':
          <strong>w trakcie</strong>
          % else:
          w trakcie
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('investment_all', _query={'filter': 'completed', 'sort': sort, 'order': order})}">
          % if filter == 'completed':
          <strong>zakończone</strong>
          % else:
          zakończone
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('investment_all', _query={'filter': 'all', 'sort': sort, 'order': order})}">
          % if filter == 'all':  
          <strong>wszystkie</strong>
          % else:
          wszystkie
          % endif
        </a>
      </div>
    </div>
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" id="sortInvestments" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Sortuj
      </button>
      <div class="dropdown-menu" aria-labelledby="sortInvestments">
        <a class="dropdown-item" href="${request.route_url('investment_all', _query={'filter': filter, 'sort': 'name', 'order': order})}">
          % if sort == 'name':
          <strong>wg nazwy</strong>
          % else:
          wg nazwy
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('investment_all', _query={'filter': filter, 'sort': 'created_at', 'order': order})}">
          % if sort == 'created_at':
          <strong>wg daty dodania</strong>
          % else:
          wg daty dodania
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('investment_all', _query={'filter': filter, 'sort': 'updated_at', 'order': order})}">
          % if sort == 'updated_at':
          <strong>wg daty edycji</strong>
          % else:
          wg daty edycji
          % endif
        </a>
      </div>
    </div>
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" id="orderInvestments" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Kolejność
      </button>
      <div class="dropdown-menu" aria-labelledby="orderInvestments">
        <a class="dropdown-item" href="${request.route_url('investment_all', _query={'filter': filter, 'sort': sort, 'order': 'asc'})}">
          % if order == 'asc':
          <strong>rosnąco</strong>
          % else:
          rosnąco
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('investment_all', _query={'filter': filter, 'sort': sort, 'order': 'desc'})}">
          % if order == 'desc':
          <strong>malejąco</strong>
          % else:
          malejąco
          % endif
        </a>
      </div>
    </div>
    <div class="float-right">
      <button type="submit" class="btn btn-success" form="investment_export" value="submit"><i class="fa fa-file-excel-o" aria-hidden="true"></i><div class="d-none d-sm-block"> Eksportuj</div></button>
    </div>
  </div>
</div>

<%include file="investment_table.mako"/>