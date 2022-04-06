<%inherit file="layout.mako"/>

<form id="branch_export" action="${request.route_url('branch_export', branch_id=branch.id)}" method="post">
  <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
  <input type="hidden" name="filter" value=${filter}>
  <input type="hidden" name="sort" value=${sort}>
  <input type="hidden" name="order" value=${order}>
</form>

<div class="card">
  <div class="card-body">
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" id="sortByVoivodeship" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        <i class="fa fa-filter" aria-hidden="true"></i> Filtruj
      </button>
      <div class="dropdown-menu" aria-labelledby="filterBranchCompanies">
        % for abbrev, name in voivodeships.items():
        <a class="dropdown-item" href="${request.route_url('branch_view', branch_id=branch.id, slug=branch.slug, _query={'filter': abbrev, 'sort': sort, 'order': order})}">
          % if filter == abbrev:
          <strong>${name}</strong>
          % else:
          ${name}
          % endif
        </a>
        % endfor
        <a class="dropdown-item" href="${request.route_url('branch_view', branch_id=branch.id, slug=branch.slug, _query={'filter': 'all', 'sort': sort, 'order': order})}">
          % if filter == 'all':
          <strong>wszystkie</strong>
          % else:
          wszystkie
          % endif
        </a>
      </div>
    </div>
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" id="sortBranchCompanies" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Sortuj
      </button>
      <div class="dropdown-menu" aria-labelledby="sortBranchCompanies">
        <a class="dropdown-item" href="${request.route_url('branch_view', branch_id=branch.id, slug=branch.slug, _query={'filter': filter, 'sort': 'name', 'order': order})}">
          % if sort == 'name':
          <strong>wg nazwy</strong>
          % else:
          wg nazwy
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('branch_view', branch_id=branch.id, slug=branch.slug, _query={'filter': filter, 'sort': 'city', 'order': order})}">
          % if sort == 'city':
          <strong>wg miasta</strong>
          % else:
          wg miasta
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('branch_view', branch_id=branch.id, slug=branch.slug, _query={'filter': filter, 'sort': 'voivodeship', 'order': order})}">
          % if sort == 'voivodeship':
          <strong>wg województwa</strong>
          % else:
          wg województwa
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('branch_view', branch_id=branch.id, slug=branch.slug, _query={'filter': filter, 'sort': 'upvotes', 'order': order})}">
          % if sort == 'upvotes':  
          <strong>wg liczby rekomendacji</strong>
          % else:
          wg liczby rekomendacji
          % endif
        </a>
      </div>
    </div>
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" id="sortBranchCompanies" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Kolejność
      </button>
      <div class="dropdown-menu" aria-labelledby="orderBranchCompanies">
        <a class="dropdown-item" href="${request.route_url('branch_view', branch_id=branch.id, slug=branch.slug, _query={'filter': filter, 'sort': sort, 'order': 'asc'})}">
          % if order == 'asc':
          <strong>rosnąco</strong>
          % else:
          rosnąco
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('branch_view', branch_id=branch.id, slug=branch.slug, _query={'filter': filter, 'sort': sort, 'order': 'desc'})}">
          % if order == 'desc':
          <strong>malejąco</strong>
          % else:
          malejąco
          % endif
        </a>
      </div>
    </div>
    <div class="float-right">
      <button type="submit" class="btn btn-success" form="branch_export" value="submit"><i class="fa fa-file-excel-o" aria-hidden="true"></i><div class="d-none d-sm-block"> Eksportuj</div></button>
      <a href="${request.route_url('branch_edit', branch_id=branch.id, slug=branch.slug)}" class="btn btn-warning" role="button"><i class="fa fa-edit" aria-hidden="true"></i><div class="d-none d-sm-block"> Edytuj</div></a>
      <button type="button" class="btn btn-danger" data-toggle="modal" data-target="#deleteModal">
        <i class="fa fa-trash" aria-hidden="true"></i><div class="d-none d-sm-block"> Usuń</div>
      </button>
    </div>
  </div>
</div>

<%include file="company_table.mako"/>

<div class="modal fade" id="deleteModal" tabindex="-1" aria-labelledby="deleteModalLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="deleteModalLabel">Usuń</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        Czy na pewno chcesz usunąć branżę z bazy danych?
      </div>
      <div class="modal-footer">
        <form action="${request.route_url('branch_delete', branch_id=branch.id, slug=branch.slug)}" method="post">
          <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
          <button type="button" class="btn btn-secondary" data-dismiss="modal">Nie</button>
          <button type="submit" class="btn btn-primary" name="submit" value="delete">Tak</button>
        </form>
      </div>
    </div>
  </div>
</div>