<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-body">
    % if investment.link:
      <a href="${investment.link}" class="btn btn-info" role="button" target="_blank"><i class="fa fa-external-link" aria-hidden="true"></i> <div class="d-none d-sm-block">Link</div></a>
    % endif
    <div class="float-right">
      <button hx-post="${request.route_url('investment_follow', investment_id=investment.id)}" hx-target="#follow" class="btn btn-secondary">
        <div id="follow">
        % if investment in request.identity.following:
          <span class="fa fa-eye fa-lg"></span>
        % else:
          <span class="fa fa-eye-slash fa-lg"></span>
        % endif
        </div>
        <div class="d-none d-sm-block">Obserwuj</div>
      </button>
      <a href="${request.route_url('investment_edit', investment_id=investment.id, slug=investment.slug)}" class="btn btn-warning" role="button"><i class="fa fa-edit" aria-hidden="true"></i> <div class="d-none d-sm-block">Edytuj</div></a>
      <button type="button" class="btn btn-danger" data-toggle="modal" data-target="#deleteModal">
        <i class="fa fa-trash" aria-hidden="true"></i> <div class="d-none d-sm-block">Usuń</div>
      </button>
    </div>
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="fa fa-briefcase" aria-hidden="true"></i> Inwestycja</div>
  <div class="card-body">
    <dl class="dl-horizontal">
      <dt>Nazwa inwestycji</dt>
      <dd>${investment.name}</dd>
      <dt>Miasto</dt>
      <dd><a href="https://maps.google.pl/maps?q=${investment.city}">${investment.city}</a></dd>
      <dt>Firma</dt>
        % if investment.company:
        <dd><a href="${request.route_url('company_view', company_id=investment.company.id, slug=investment.company.slug)}">${investment.company.name}</a></dd>
        % else:
        <dd>---</dd>
        % endif
      <dt>Termin</dt>
      <dd>${investment.deadline}</dd>
    </dl>
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="fa fa-clock-o" aria-hidden="true"></i> Data modyfikacji</div>
  <div class="card-body">
    <p>
      Utworzono: ${investment.created_at.strftime('%Y-%m-%d %H:%M:%S')}
      % if investment.created_by:
        przez <a href="${request.route_url('user_view', username=investment.created_by.username, what='info')}">${investment.created_by.username}</a>
      % endif
      <br>
      % if investment.updated_at:
        Zmodyfikowano: ${investment.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if investment.updated_by:
          przez <a href="${request.route_url('user_view', username=investment.updated_by.username, what='info')}">${investment.updated_by.username}</a>
        % endif
      % endif
    </p>
  </div>
</div>

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
        Czy na pewno chcesz usunąć inwestycję z bazy danych?
      </div>
      <div class="modal-footer">
        <form action="${request.route_url('investment_delete', investment_id=investment.id, slug=investment.slug)}" method="post">
          <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
          <button type="button" class="btn btn-secondary" data-dismiss="modal">Nie</button>
          <button type="submit" class="btn btn-primary" name="submit" value="delete">Tak</button>
        </form>
      </div>
    </div>
  </div>
</div>