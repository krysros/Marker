<%inherit file="layout.mako"/>

<div class="card">
  <div class="card-body">
    <div class="btn-group">
      <button class="btn btn-secondary dropdown-toggle" type="button" id="sortByVoivodeship" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        <i class="fa fa-filter" aria-hidden="true"></i> Filtruj
      </button>
      <div class="dropdown-menu" aria-labelledby="sortByVoivodeship">
        % for abbrev, name in voivodeships.items():
        <a class="dropdown-item" href="${request.route_url('company_similar', company_id=company.id, slug=company.slug, _query={'filter': abbrev})}">
          % if filter == abbrev:
          <strong>${name}</strong>
          % else:
          ${name}
          % endif
        </a>
        % endfor
        <a class="dropdown-item" href="${request.route_url('company_similar', company_id=company.id, slug=company.slug, _query={'filter': 'all'})}">
          % if filter == 'all':
          <strong>wszystkie</strong>
          % else:
          wszystkie
          % endif
        </a>
      </div>
    </div>
  </div>
</div>

<p class="lead">Firmy o profilu działalności zbliżonym do <a href="${request.route_url('company_view', company_id=company.id, slug=company.slug)}">${company.name}</a></p>
<%include file="company_table.mako"/>