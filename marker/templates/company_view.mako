<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-body">
    <div class="btn-group">
      <button class="btn btn-primary dropdown-toggle" type="button" id="dropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        Dokument
      </button>
      <div class="dropdown-menu" aria-labelledby="dropdownMenuLink">
        <a class="dropdown-item" href="${request.route_url('contract', company_id=company.id, slug=company.slug)}" class="btn btn-primary" role="button"><i class="fa fa-file-word-o" aria-hidden="true"></i> Umowa</a>
        <a class="dropdown-item" href="${request.route_url('envelope', company_id=company.id, slug=company.slug)}"><i class="fa fa-envelope-o" aria-hidden="true"></i> Koperta</a>
      </div>
    </div>
    <div class="float-right">
      <button hx-post="${request.route_url('company_upvote', company_id=company.id)}" hx-target="#upvote" class="btn btn-secondary">
        <div id="upvote">
        % if company in request.identity.upvotes:
          <span class="fa fa-thumbs-up fa-lg"></span>
        % else:
          <span class="fa fa-thumbs-o-up fa-lg"></span>
        % endif
        </div>
        <div class="d-none d-sm-block"> Rekomendacja</div>
      </button>
      <a href="${request.route_url('company_edit', company_id=company.id, slug=company.slug)}" class="btn btn-warning" role="button"><i class="fa fa-edit" aria-hidden="true"></i><div class="d-none d-sm-block"> Edytuj</div></a>
      <button type="button" class="btn btn-danger" data-toggle="modal" data-target="#deleteModal">
        <i class="fa fa-trash" aria-hidden="true"></i><div class="d-none d-sm-block"> Usuń</div>
      </button>
    </div>
  </div>
</div>

<div class="card border-${company.category}">
  <div class="card-header">
    <i class="fa fa-industry" aria-hidden="true"></i> Firma
    <div class="float-right">
      <div class="form-check">
        % if company in request.identity.marker:
        <input type="checkbox"
               value="${company.id}"
               autocomplete="off"
               checked
               hx-post="${request.route_url('company_mark', company_id=company.id)}"
               hx-trigger="click"
               hx-swap="none">
        % else:
        <input type="checkbox"
               value="${company.id}"
               autocomplete="off"
               hx-post="${request.route_url('company_mark', company_id=company.id)}"
               hx-trigger="click"
               hx-swap="none">
        % endif
        <label class="form-check-label" for="mark">Zaznacz</label>
      </div>
    </div>
  </div>
  <div class="card-body">
    <h1 class="pb-4">${company.name}</h1>
    <div class="row">
      <div class="col-md-4">
        <address>
          <h3><i class="fa fa-map-marker" aria-hidden="true"></i> Adres</h3>
          ${company.street}<br>
          % if company.postcode:
          ${company.postcode} ${company.city}<br>
          % else:
          ${company.city}<br>
          % endif
          ${voivodeships.get(company.voivodeship)}<br>
          % if company.street and company.city:
          <a href="https://maps.google.pl/maps?q=${company.street}+${company.city}">Pokaż na mapie</a>
          % elif company.city:
          <a href="https://maps.google.pl/maps?q=${company.city}">Pokaż na mapie</a>
          % endif
        </address>
      </div>
      <div class="col-md-4">
        <address>
          <h3><i class="fa fa-phone" aria-hidden="true"></i> Kontakt</h3>
          <abbr title="Telefon">T:</abbr> ${company.phone}<br>
          <abbr title="Email">E:</abbr> <a href="mailto:${company.email}">${company.email}</a><br>
          <abbr title="WWW">W:</abbr>
          % if company.www.startswith('http'):
            <a href="${company.www}">
          % else:
            <a href="${'http://' + company.www}">
          % endif
          ${company.www}</a>
        </address>
      </div>
      <div class="col-md-4">
        <h3><i class="fa fa-certificate" aria-hidden="true"></i> Dane rejestrowe</h3>
        NIP: ${company.nip or "brak"}<br>
        REGON: ${company.regon or "brak"}<br>
        KRS: ${company.krs or "brak"}
        % if company.court:
          <br>${courts.get(company.court)}
        % endif
      </div>
    </div>
  </div>
  <div class="card-footer">
    <ul class="nav">
      <li class="nav-item">
        % if c_comments:
        <a class="nav-link text-warning" href="${request.route_url('company_comments', company_id=company.id, slug=company.slug)}">Komentarze (${c_comments})</a>
        % else:
        <a class="nav-link" href="${request.route_url('company_comments', company_id=company.id, slug=company.slug)}">Komentarze (${c_comments})</a>
        % endif
      </li>
      <li class="nav-item">
        % if c_upvotes:
        <a class="nav-link text-success" href="${request.route_url('company_upvotes', company_id=company.id, slug=company.slug)}">Rekomendacje (${c_upvotes})</a>
        % else:
        <a class="nav-link" href="${request.route_url('company_upvotes', company_id=company.id, slug=company.slug)}">Rekomendacje (${c_upvotes})</a>
        % endif
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_investments', company_id=company.id, slug=company.slug)}">Inwestycje (${c_investments})</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="${request.route_url('company_similar', company_id=company.id, slug=company.slug)}">Podobne (${c_similar})</a>
      </li>
    </ul>
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="fa fa-cubes" aria-hidden="true"></i> Branże</div>
  <div class="card-body">
    <div class="table-responsive">
      <table class="table table-striped">
        <thead>
          <tr>
            <th>Branża</th>
          </tr>
        </thead>
        <tbody>
          % for branch in company.branches:
          <tr>
            <td><a href="${request.route_url('branch_view', branch_id=branch.id, slug=branch.slug)}">${branch.name}</a></td>
          </tr>
          % endfor
        </tbody>
      </table>
    </div>
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="fa fa-group" aria-hidden="true"></i> Osoby do kontaktu</div>
  <div class="card-body">
    <div class="table-responsive">
      <table class="table table-striped">
        <thead>
          <tr>
            <th>Imię i nazwisko</th>
            <th>Stanowisko</th>
            <th>Telefon</th>
            <th>Email</th>
            <th>Wizytówka</th>
          </tr>
        </thead>
        <tbody>
          % for person in company.people:
          <tr>
            <td>${person.fullname}</a></td>
            <td>${person.position}</td>
            <td>${person.phone}</td>
            <td><a href="mailto:${person.email}">${person.email}</a></td>
            <td>
              <form action="${request.route_url('person_vcard', person_id=person.id)}" method="post">
                <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
                <button type="submit" class="btn btn-default" value="submit"><i class="fa fa-address-card" aria-hidden="true"></i></button>
              </form>
            </td>
          </tr>
          % endfor
        </tbody>
      </table>
    </div>
  </div>
</div>

<div class="card">
  <div class="card-header"><i class="fa fa-clock-o" aria-hidden="true"></i> Data modyfikacji</div>
  <div class="card-body">
    <p>
      Utworzono: ${company.created_at.strftime('%Y-%m-%d %H:%M:%S')}
      % if company.created_by:
        przez <a href="${request.route_url('user_view', username=company.created_by.username, what='info')}">${company.created_by.username}</a>
      % endif
      <br>
      % if company.updated_at:
        Zmodyfikowano: ${company.updated_at.strftime('%Y-%m-%d %H:%M:%S')}
        % if company.updated_by:
          przez <a href="${request.route_url('user_view', username=company.updated_by.username, what='info')}">${company.updated_by.username}</a>
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
        Czy na pewno chcesz usunąć firmę z bazy danych?
      </div>
      <div class="modal-footer">
        <form action="${request.route_url('company_delete', company_id=company.id, slug=company.slug)}" method="post">
          <input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
          <button type="button" class="btn btn-secondary" data-dismiss="modal">Nie</button>
          <button type="submit" class="btn btn-primary" name="submit" value="delete">Tak</button>
        </form>
      </div>
    </div>
  </div>
</div>