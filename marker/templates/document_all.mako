<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-body">
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" id="filterDocuments" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        <i class="fa fa-filter" aria-hidden="true"></i> Filtruj
      </button>
      <div class="dropdown-menu" aria-labelledby="filterDocuments">
        % for typ, typ_name in doctypes.items():
        <a class="dropdown-item" href="${request.route_url('document_all', _query={'filter': typ, 'sort': sort, 'order': order})}">
          % if filter == typ:
          <strong>${typ_name}</strong>
          % else:
          ${typ_name}
          % endif
        </a>
        % endfor
        <a class="dropdown-item" href="${request.route_url('document_all', _query={'filter': 'all', 'sort': sort, 'order': order})}">
          % if filter == 'all':
          <strong>wszystkie</strong>
          % else:
          wszystkie
          % endif
        </a>
      </div>
    </div>
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" id="sortDocuments" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Sortuj
      </button>
      <div class="dropdown-menu" aria-labelledby="sortDocuments">
        <a class="dropdown-item" href="${request.route_url('document_all', _query={'filter': filter, 'sort': 'filename', 'order': order})}">
          % if sort == 'filename':
          <strong>wg nazwy</strong>
          % else:
          wg nazwy
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('document_all', _query={'filter': filter, 'sort': 'added', 'order': order})}">
          % if sort == 'added':
          <strong>wg daty dodania</strong>
          % else:
          wg daty dodania
          % endif
        </a>
      </div>
    </div>
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" id="orderDocuments" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Kolejność
      </button>
      <div class="dropdown-menu" aria-labelledby="orderDocuments">
        <a class="dropdown-item" href="${request.route_url('document_all', _query={'filter': filter, 'sort': sort, 'order': 'asc'})}">
          % if order == 'asc':
          <strong>rosnąco</strong>
          % else:
          rosnąco
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('document_all', _query={'filter': filter, 'sort': sort, 'order': 'desc'})}">
          % if order == 'desc':
          <strong>malejąco</strong>
          % else:
          malejąco
          % endif
        </a>
      </div>
    </div>
    <div class="float-right">
      <a href="${request.route_url('document_upload')}" class="btn btn-primary" role="button"><i class="fa fa-upload" aria-hidden="true"></i><div class="d-none d-sm-block"> Prześlij</div></a>
    </div>
  </div>
</div>

<%include file="document_table.mako"/>