<%inherit file="layout.mako"/>

<form id="user_following_export" action="${request.route_url('user_following_export', username=user.username)}" method="post">
  <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
  <input type="hidden" name="filter" value=${filter}>
  <input type="hidden" name="sort" value=${sort}>
  <input type="hidden" name="order" value=${order}>
</form>

<div class="card">
  <div class="card-body">
    <div class="btn-group">
      <button type="button" class="btn btn-secondary dropdown-toggle" data-toggle="dropdown" aria-expanded="false">
        <i class="fa fa-filter" aria-hidden="true"></i> Filtruj
      </button>
      <div class="dropdown-menu" role="menu">
        <a class="dropdown-item" href="${request.route_url('user_following', username=user.username, _query={'filter': 'inprogress', 'sort': sort, 'order': order})}">
          % if filter == 'inprogress':
          <strong>w trakcie</strong>
          % else:
          w trakcie
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('user_following', username=user.username, _query={'filter': 'completed', 'sort': sort, 'order': order})}">
          % if filter == 'completed':
          <strong>zakończone</strong>
          % else:
          zakończone
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('user_following', username=user.username, _query={'filter': 'all', 'sort': sort, 'order': order})}">
          % if filter == 'all':
          <strong>wszystkie</strong>
          % else:
          wszystkie
          % endif
        </a>
      </div>
    </div>
    <div class="btn-group">
      <button type="button" class="btn btn-secondary dropdown-toggle" data-toggle="dropdown" aria-expanded="false">
        Sortuj
      </button>
      <div class="dropdown-menu" role="menu">
        <a class="dropdown-item" href="${request.route_url('user_following', username=user.username, _query={'filter': filter, 'sort': 'added', 'order': order})}">
          % if sort == 'added':
          <strong>wg daty dodania</strong>
          % else:
          wg daty dodania
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('user_following', username=user.username, _query={'filter': filter, 'sort': 'edited', 'order': order})}">
          % if sort == 'edited':
          <strong>wg daty edycji</strong>
          % else:
          wg daty edycji
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('user_following', username=user.username, _query={'filter': filter, 'sort': 'name', 'order': order})}">
          % if sort == 'name':
          <strong>alfabetycznie</strong>
          % else:
          alfabetycznie
          % endif
        </a>
      </div>
    </div>
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" id="userFollowing" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Kolejność
      </button>
      <div class="dropdown-menu" aria-labelledby="userFollowing">
        <a class="dropdown-item" href="${request.route_url('user_following', username=user.username, _query={'filter': filter, 'sort': sort, 'order': 'asc'})}">
          % if order == 'asc':
          <strong>rosnąco</strong>
          % else:
          rosnąco
          % endif
        </a>
        <a class="dropdown-item" href="${request.route_url('user_following', username=user.username, _query={'filter': filter, 'sort': sort, 'order': 'desc'})}">
          % if order == 'desc':
          <strong>malejąco</strong>
          % else:
          malejąco
          % endif
        </a>
      </div>
    </div>
    <div class="float-right">
      <button type="submit" class="btn btn-success" form="user_following_export" value="submit"><i class="fa fa-file-excel-o" aria-hidden="true"></i><div class="d-none d-sm-block"> Eksportuj</div></button>
      <button type="button" class="btn btn-danger" data-toggle="modal" data-target="#clearModal">
        <i class="fa fa-eye-slash" aria-hidden="true"></i><div class="d-none d-sm-block"> Wyczyść</div>
      </button>  
    </div>
  </div>
</div>

<%include file="investment_table.mako"/>

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
        Wyczyścić wszystkie obserwowane inwestycje?<br>Ta operacja nie usuwa inwestycji z bazy danych. 
      </div>
      <div class="modal-footer">
        <form action="${request.route_url('user_following_clear', username=user.username)}" method="post">
          <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
          <button type="button" class="btn btn-secondary" data-dismiss="modal">Nie</button>
          <button type="submit" class="btn btn-primary" name="submit" value="delete">Tak</button>
        </form>
      </div>
    </div>
  </div>
</div>