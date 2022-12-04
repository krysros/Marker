<%inherit file="layout.mako"/>
<%namespace name="button" file="button.mako"/>

<div class="p-4 mb-4 bg-light rounded-3">
  <div class="container">
    <h1>${project} <small class="text-muted">Informacje o firmach i projektach</small></h1>
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
        ${button.show('company_all')}
        ${button.search('company_search')}
        ${button.add('company_add')}
      </p>
    </div>
    <div class="col">
      <h2><i class="bi bi-briefcase"></i> Projekty</h2>
      <p>
        Realizowane lub zakończone projekty.
      </p>
      <p>
        ${button.show('project_all')}
        ${button.search('project_search')}
        ${button.add('project_add')}
      </p>
    </div>
    <div class="col">
      <h2><i class="bi bi-tags"></i> Tagi</h2>
      <p>
        Tagi określają profil działalności firmy.
      </p>
      <p>
        ${button.show('tag_all')}
        ${button.search('tag_search')}
        ${button.add('tag_add')}
      </p>
    </div>
  </div>
  <div class="row">
    <div class="col">
      <h2><i class="bi bi-chat-left-text"></i> Komentarze</h2>
      <p>
        Komentarze dotyczące firm.
      </p>
      <p>
        ${button.show('comment_all')}
        ${button.search('comment_search')}
      </p>
    </div>
    <div class="col">
      <h2><i class="bi bi-bar-chart"></i> Raporty</h2>
      <p>
        Podsumowanie informacji o firmach i projektach.
      </p>
      <p>
        ${button.show('report')}
      </p>
    </div>
    <div class="col">
      <h2><i class="bi bi-person-circle"></i> Użytkownicy</h2>
      <p>
        Użytkownicy aplikacji.
      </p>
      <p>
        ${button.show('user_all')}
        ${button.search('user_search')}
        ${button.add('user_add')}
      </p>
    </div>
  </div>
</div>