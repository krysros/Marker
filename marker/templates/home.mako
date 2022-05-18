<%inherit file="layout.mako"/>

<div class="jumbotron">
  <h1>Marker <small class="text-muted">Informacje o firmach i inwestycjach</small></h1>
  <p class="lead">
    Znajdź najczęściej rekomendowane firmy o określonym profilu działalności.
    Sprawdź, które firmy zrealizowały największą liczbę inwestycji,
    które regiony są najbardziej przedsiębiorcze
    i w jakich branżach jest największa konkurencja.
  </p>
</div>

<div class="container">
  <div class="row">
    <div class="col-sm">
      <h2><i class="fa fa-cubes" aria-hidden="true"></i> Branże</h2>
      <p>
        Pokaż listę branż oraz firmy o określonym profilu działalności.
      </p>
      <p><a class="btn btn-secondary" href="${request.route_url('branch_all')}" role="button">Pokaż &raquo;</a></p>
    </div>
    <div class="col-sm">
      <h2><i class="fa fa-industry" aria-hidden="true"></i> Firmy</h2>
      <p>
        Wyświetl listę firm ostatnio dodanych do bazy danych.
        Pokaż firmy, których dane zostały ostatnio zmienione.
      </p>
      <p><a class="btn btn-secondary" href="${request.route_url('company_all')}" role="button">Pokaż &raquo;</a></p>
    </div>
    <div class="col-sm">
      <h2><i class="fa fa-briefcase" aria-hidden="true"></i> Inwestycje</h2>
      <p>
        Pokaż listę inwestycji. Filtruj inwestycje, aby wyświetlić te,
        które są w trakcie lub zostały zakończone.
      </p>
      <p><a class="btn btn-secondary" href="${request.route_url('investment_all')}" role="button">Pokaż &raquo;</a></p>
    </div>
  </div>

  <div class="row">
    <div class="col-sm">
      <h2><i class="fa fa-line-chart" aria-hidden="true"></i> Raporty</h2>
      <p>
        Wyświetl podsumowanie zawartości bazy danych.
        Analizuj dane o firmach i inwestycjach.
      </p>
      <p><a class="btn btn-secondary" href="${request.route_url('report')}" role="button">Pokaż &raquo;</a></p>
    </div>
    <div class="col-sm">
      <h2><i class="fa fa-file-word-o" aria-hidden="true"></i> Dokumenty</h2>
      <p>
        Generuj dokumenty w postaci plików Worda wykorzystując szablony i dane z bazy.
      </p>
    </div>
    <div class="col-sm">
      <h2><i class="fa fa-file-excel-o" aria-hidden="true"></i> Eksport</h2>
      <p>
        Wyeksportuj wybrane dane kontaktowe do Excela.
        Skorzystaj z korespondencji seryjnej.
      </p>
    </div>
  </div>
</div>