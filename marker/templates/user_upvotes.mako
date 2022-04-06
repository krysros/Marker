<%inherit file="layout.mako"/>

<form id="user_upvotes_export" action="${request.route_url('user_upvotes_export', username=user.username)}" method="post">
  <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
  <input type="hidden" name="sort" value=${sort}>
  <input type="hidden" name="order" value=${order}>
</form>

<div class="card">
  <div class="card-body">
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" data-toggle="dropdown" aria-expanded="false">
        Sortuj
      </button>
      <div class="dropdown-menu" dropdown-menu>
        <a class="dropdown-item" href="${request.route_url('user_upvotes', username=user.username, _query={'sort': 'name', 'order': order})}">
          % if sort == 'name':
          <strong>wg nazwy</strong>
          % else:
          wg nazwy
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('user_upvotes', username=user.username, _query={'sort': 'city', 'order': order})}">
          % if sort == 'city':
          <strong>wg miasta</strong>
          % else:
          wg miasta
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('user_upvotes', username=user.username, _query={'sort': 'voivodeship', 'order': order})}">
          % if sort == 'voivodeship':
          <strong>wg województwa</strong>
          % else:
          wg województwa
          % endif
        </a>
      </div>
    </div>
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" id="userUpvotes" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Kolejność
      </button>
      <div class="dropdown-menu" aria-labelledby="userUpvotes">
        <a class="dropdown-item" href="${request.route_url('user_upvotes', username=user.username, _query={'sort': sort, 'order': 'asc'})}">
          % if order == 'asc':
          <strong>rosnąco</strong>
          % else:
          rosnąco
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('user_upvotes', username=user.username, _query={'sort': sort, 'order': 'desc'})}">
          % if order == 'desc':
          <strong>malejąco</strong>
          % else:
          malejąco
          % endif
        </a>
      </div>
    </div>
    <div class="float-right">
      <button type="submit" class="btn btn-success" form="user_upvotes_export" value="submit"><i class="fa fa-file-excel-o" aria-hidden="true"></i><div class="d-none d-sm-block"> Eksportuj</div></button>
      <button type="button" class="btn btn-danger" data-toggle="modal" data-target="#clearModal">
        <i class="fa fa-thumbs-o-up" aria-hidden="true"></i><div class="d-none d-sm-block"> Wyczyść</div>
      </button>  
    </div>
  </div>
</div>

<%include file="company_table.mako"/>

<div class="modal fade" id="clearModal" tabindex="-1" aria-labelledby="clearModalLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="clearModalLabel">Wyczyść</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        Wyczyścić wszystkie rekomendacje?<br>Ta operacja nie usuwa firm z bazy danych. 
      </div>
      <div class="modal-footer">
        <form action="${request.route_url('user_upvotes_clear', username=user.username)}" method="post">
          <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
          <button type="button" class="btn btn-secondary" data-dismiss="modal">Nie</button>
          <button type="submit" class="btn btn-primary" name="submit" value="delete">Tak</button>
        </form>
      </div>
    </div>
  </div>
</div>