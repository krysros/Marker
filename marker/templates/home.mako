<%inherit file="layout.mako"/>

<div class="p-4 mb-4 bg-light rounded-3">
  <div class="container">
    <h1>Marker <small class="text-muted">Informacje o firmach i projektach</small></h1>
    <p class="fs-4">
      Znajdź najczęściej rekomendowane firmy o określonym profilu działalności.
      Sprawdź, które firmy zrealizowały największą liczbę projektów,
      które regiony są najbardziej przedsiębiorcze
      i w jakich branżach jest największa konkurencja.
    </p>
  </div>
</div>

<div class="container">
  <div class="row">
    <div class="col">
      <h2><i class="bi bi-building"></i> Firmy</h2>
      <p>
        Ostatnio dodane firmy wg wybranej kategorii.
      </p>
      <p>
        <a class="btn btn-secondary" href="${request.route_url('company_all')}" role="button">Pokaż</a>
        <a class="btn btn-primary" href="${request.route_url('company_search')}" role="button">Szukaj</a>
        <a class="btn btn-success" href="${request.route_url('company_add')}" role="button">Dodaj</a>
      </p>
    </div>
    <div class="col">
      <h2><i class="bi bi-briefcase"></i> Projekty</h2>
      <p>
        Realizowane lub zakończone projekty.
      </p>
      <p>
        <a class="btn btn-secondary" href="${request.route_url('project_all')}" role="button">Pokaż</a>
        <a class="btn btn-primary" href="${request.route_url('project_search')}" role="button">Szukaj</a>
        <a class="btn btn-success" href="${request.route_url('project_add')}" role="button">Dodaj</a>
      </p>
    </div>
    <div class="col">
      <h2><i class="bi bi-tags"></i> Tagi</h2>
      <p>
        Tagi określają profil działalności firmy.
      </p>
      <p>
        <a class="btn btn-secondary" href="${request.route_url('tag_all')}" role="button">Pokaż</a>
        <a class="btn btn-primary" href="${request.route_url('tag_search')}" role="button">Szukaj</a>
        <a class="btn btn-success" href="${request.route_url('tag_add')}" role="button">Dodaj</a>
      </p>
    </div>
  </div>
  <div class="row">
    <div class="col">
      <h2><i class="bi bi-person-circle"></i> Użytkownicy</h2>
      <p>
        Użytkownicy aplikacji.
      </p>
      <p>
        <a class="btn btn-secondary" href="${request.route_url('user_all')}" role="button">Pokaż</a>
        <a class="btn btn-primary" href="${request.route_url('user_search')}" role="button">Szukaj</a>
        <a class="btn btn-success" href="${request.route_url('user_add')}" role="button">Dodaj</a>
      </p>
    </div>
    <div class="col">
      <h2><i class="bi bi-chat-left-text"></i> Komentarze</h2>
      <p>
        Komentarze dotyczące firm.
      </p>
      <p>
        <a class="btn btn-secondary" href="${request.route_url('comment_all')}" role="button">Pokaż</a>
        <a class="btn btn-primary" href="${request.route_url('comment_search')}" role="button">Szukaj</a>
      </p>
    </div>
    <div class="col">
      <h2><i class="bi bi-bar-chart"></i> Raporty</h2>
      <p>
        Podsumowanie informacji o firmach i projektach.
      </p>
      <p><a class="btn btn-secondary" href="${request.route_url('report')}" role="button">Pokaż</a></p>
    </div>
  </div>
</div>