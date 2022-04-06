<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-body">
    % if tender.link:
      <a href="${tender.link}" class="btn btn-info" role="button" target="_blank"><i class="fa fa-external-link" aria-hidden="true"></i> <div class="d-none d-sm-block">Ogłoszenie</div></a>
    % endif
    <div class="float-right">
      <button hx-post="${request.route_url('tender_follow', tender_id=tender.id)}" hx-target="#follow" class="btn btn-secondary">
        <div id="follow">
        % if tender in request.identity.following:
          <span class="fa fa-eye fa-lg"></span>
        % else:
          <span class="fa fa-eye-slash fa-lg"></span>
        % endif
        </div>
        <div class="d-none d-sm-block">Obserwuj</div>
      </button>
      <a href="${request.route_url('tender_edit', tender_id=tender.id, slug=tender.slug)}" class="btn btn-warning" role="button"><i class="fa fa-edit" aria-hidden="true"></i> <div class="d-none d-sm-block">Edytuj</div></a>
      <button type="button" class="btn btn-danger" data-toggle="modal" data-target="#deleteModal">
        <i class="fa fa-trash" aria-hidden="true"></i> <div class="d-none d-sm-block">Usuń</div>
      </button>
    </div>
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="fa fa-briefcase" aria-hidden="true"></i> Przetarg</div>
  <div class="card-body">
    <dl class="dl-horizontal">
      <dt>Nazwa przetargu</dt>
      <dd>${tender.name}</dd>
      <dt>Miasto</dt>
      <dd><a href="https://maps.google.pl/maps?q=${tender.city}">${tender.city}</a></dd>
      <dt>Zamawiający</dt>
        % if tender.company:
        <dd><a href="${request.route_url('company_view', company_id=tender.company.id, slug=tender.company.slug)}">${tender.company.name}</a></dd>
        % else:
        <dd>---</dd>
        % endif
      <dt>Termin składania ofert</dt>
      <dd>${tender.deadline}</dd>
    </dl>
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="fa fa-clock-o" aria-hidden="true"></i> Data modyfikacji</div>
  <div class="card-body">
    <p>
      Utworzono: ${tender.added.strftime('%Y-%m-%d %H:%M:%S')}
      % if tender.added_by:
        przez <a href="${request.route_url('user_view', username=tender.added_by.username, what='info')}">${tender.added_by.username}</a>
      % endif
      <br>
      % if tender.edited:
        Zmodyfikowano: ${tender.edited.strftime('%Y-%m-%d %H:%M:%S')}
        % if tender.edited_by:
          przez <a href="${request.route_url('user_view', username=tender.edited_by.username, what='info')}">${tender.edited_by.username}</a>
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
        Czy na pewno chcesz usunąć przetarg z bazy danych?
      </div>
      <div class="modal-footer">
        <form action="${request.route_url('tender_delete', tender_id=tender.id, slug=tender.slug)}" method="post">
          <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
          <button type="button" class="btn btn-secondary" data-dismiss="modal">Nie</button>
          <button type="submit" class="btn btn-primary" name="submit" value="delete">Tak</button>
        </form>
      </div>
    </div>
  </div>
</div>